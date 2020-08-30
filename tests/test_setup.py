import unittest
import setup
import logging
import os
import yaml
import datetime
from io import StringIO
import sys

TEST_RESULT_LOG_FILE_PATH = "tests/logs/test_result.log"
SETUP_CONFIG_FILE_PATH = "config/setup-config.yaml"
AWS_ALL_REGIONS = [
    "us-east-2",
    "us-east-1",
    "us-west-1",
    "us-west-2",
    "af-south-1",
    "ap-east-1",
    "ap-south-1",
    "ap-northeast-3",
    "ap-northeast-2",
    "ap-northeast-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "ca-central-1",
    "eu-central-1",
    "eu-west-1",
    "eu-west-2",
    "eu-south-1",
    "eu-west-3",
    "eu-north-1",
    "me-south-1",
    "sa-east-1",
]
CLI_ALL_OUTPUT_FORMATS = ["json", "yaml", "text", "table"]
BASH_LOGIN_SHELL_SETTING_FILE_PATH = "$HOME/.bashrc"
ZSH_LOGIN_SHELL_SETTING_FILE_PATH = "$HOME/.zshrc"
REGISTER_STS_ASSUMED_ROLE_BASH_TEMPLATE_FILE_PATH = (
    "template/register_sts_assumed_role.bash.tmpl"
)
REGISTER_STS_ASSUMED_ROLE_ZSH_TEMPLATE_FILE_PATH = (
    "template/register_sts_assumed_role.zsh.tmpl"
)
REPLACEMENT_STRING_CONFIG_FILE_PATH = "$REPLACEMENT_STRING_CONFIG_FILE_PATH"
REPLACEMENT_STRING_REGISTER_PROFILE = "$REPLACEMENT_STRING_REGISTER_PROFILE"
REPLACEMENT_STRING_REGION_NAME = "$REPLACEMENT_STRING_REGION_NAME"
REPLACEMENT_STRING_OUTPUT_FORMAT = "$REPLACEMENT_STRING_OUTPUT_FORMAT"
REPLACEMENT_STRING_CHANGE_LOG_FILE_PATH = "$REPLACEMENT_STRING_CHANGE_LOG_FILE_PATH"
REGISTER_STS_ASSUMED_ROLE_START_SIGNAL = (
    "###### register_sts_assumed_role starts here ######"
)
REGISTER_STS_ASSUMED_ROLE_END_SIGNAL = (
    "###### register_sts_assumed_role ends here ######"
)


class TestSetup(unittest.TestCase):
    logger = None

    @classmethod
    def setUpClass(cls):
        cls.__initialize_logger()

    @classmethod
    def __initialize_logger(cls):
        if not os.path.isdir("tests/logs"):
            os.makedirs("tests/logs")
        global logger
        logging.basicConfig(filename=TEST_RESULT_LOG_FILE_PATH)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

    def test_load_setup_config_all_values_must_be_available(self):
        ## given
        with open(SETUP_CONFIG_FILE_PATH, "r") as config_file:
            config = yaml.load(config_file, Loader=yaml.SafeLoader)["setup"]
            config_file_path = config["config_file"]["file_path"]

            register_profile = config["register_profile"]
            profile_name = register_profile["profile_name"]["default"]
            region = register_profile["region"]["default"]
            output = register_profile["output"]["default"]

            change_log_file_path = config["change_log"]["file_path"]

        ## when
        config = setup.load_setup_config(setup.SETUP_CONFIG_FILE_PATH)

        ## then
        self.assertTrue(len(config.config_file_path) > 0)
        self.assertEqual(config.config_file_path, config_file_path)
        self.assertTrue(len(config.profile_name) > 0)
        self.assertEqual(config.profile_name, profile_name)
        self.assertTrue(len(config.region) > 0)
        self.assertEqual(config.region, region)
        self.assertTrue(len(config.output) > 0)
        self.assertEqual(config.output, output)
        self.assertTrue(len(config.change_log_file_path) > 0)
        self.assertEqual(config.change_log_file_path, change_log_file_path)

    def test_load_setup_config_expected_value(self):
        ## when
        config = setup.load_setup_config(SETUP_CONFIG_FILE_PATH)

        ## then
        self.assertIn(config.region, AWS_ALL_REGIONS)
        self.assertIn(config.output, CLI_ALL_OUTPUT_FORMATS)

    def test_get_login_shell_setting_file_path_expected_value(self):
        ## given
        login_shells = [
            {
                "login_shell_path": "/bin/bash",
                "expected_value": BASH_LOGIN_SHELL_SETTING_FILE_PATH.replace(
                    "$HOME", os.environ["HOME"]
                ),
            },
            {
                "login_shell_path": "/usr/local/bin/zsh",
                "expected_value": ZSH_LOGIN_SHELL_SETTING_FILE_PATH.replace(
                    "$HOME", os.environ["HOME"]
                ),
            },
            {
                "login_shell_path": "test",
                "expected_value": "test_login_shell_setting_file_path.rc",
            },
            {"login_shell_path": "/bin/tcsh", "expected_value": None},
            {"login_shell_path": None, "expected_value": None},
        ]

        for login_shell in login_shells:
            ## when
            login_shell_setting_file_path = setup.get_login_shell_setting_file_path(
                login_shell["login_shell_path"]
            )

            ## then
            self.assertEqual(
                login_shell_setting_file_path, login_shell["expected_value"]
            )

    def test_get_register_sts_assumed_role_template_file_path_expected_value(self):
        ## given
        login_shells = [
            {
                "login_shell_path": "/bin/bash",
                "expected_value": REGISTER_STS_ASSUMED_ROLE_BASH_TEMPLATE_FILE_PATH,
            },
            {
                "login_shell_path": "/usr/local/bin/zsh",
                "expected_value": REGISTER_STS_ASSUMED_ROLE_ZSH_TEMPLATE_FILE_PATH,
            },
            {
                "login_shell_path": "test",
                "expected_value": REGISTER_STS_ASSUMED_ROLE_BASH_TEMPLATE_FILE_PATH,
            },
            {"login_shell_path": "/bin/tcsh", "expected_value": None},
            {"login_shell_path": None, "expected_value": None},
        ]

        for login_shell in login_shells:
            ## when
            register_sts_assumed_role_template_file_path = setup.get_register_sts_assumed_role_template_file_path(
                login_shell["login_shell_path"]
            )

            ## then
            self.assertEqual(
                register_sts_assumed_role_template_file_path,
                login_shell["expected_value"],
            )

    def test_generate_register_sts_assumed_role_template_expected_value(self):
        ## given
        with open(
            REGISTER_STS_ASSUMED_ROLE_BASH_TEMPLATE_FILE_PATH, "r"
        ) as bash_template_file:
            bash_expected_value = bash_template_file.read()
        with open(
            REGISTER_STS_ASSUMED_ROLE_ZSH_TEMPLATE_FILE_PATH, "r"
        ) as zsh_template_file:
            zsh_expected_value = zsh_template_file.read()

        login_shells = [
            {"login_shell_path": "/bin/bash", "expected_value": bash_expected_value},
            {
                "login_shell_path": "/usr/local/bin/zsh",
                "expected_value": zsh_expected_value,
            },
        ]
        for login_shell in login_shells:
            login_shell["expected_value"] = (
                login_shell["expected_value"]
                .replace(REPLACEMENT_STRING_CONFIG_FILE_PATH, "$HOME/.aws/config")
                .replace(REPLACEMENT_STRING_REGISTER_PROFILE, "sts-session")
                .replace(REPLACEMENT_STRING_REGION_NAME, "ap-northeast-1")
                .replace(REPLACEMENT_STRING_OUTPUT_FORMAT, "json")
                .replace(
                    REPLACEMENT_STRING_CHANGE_LOG_FILE_PATH,
                    "$HOME/.aws/sts_assumed_role.log",
                )
            )

        ## when
        for login_shell in login_shells:
            str_register_sts_assumed_role = setup.generate_register_sts_assumed_role_template(
                setup.get_register_sts_assumed_role_template_file_path(
                    login_shell["login_shell_path"]
                ),
                setup.load_setup_config(setup.SETUP_CONFIG_FILE_PATH),
            )

            ## then
            self.assertEqual(
                str_register_sts_assumed_role, login_shell["expected_value"]
            )

    def test_replace_replacement_string(self):
        template_file_paths = [
            setup.REGISTER_STS_ASSUMED_ROLE_BASH_TEMPLATE_FILE_PATH,
            setup.REGISTER_STS_ASSUMED_ROLE_ZSH_TEMPLATE_FILE_PATH,
        ]
        for template_file_path in template_file_paths:
            ## given
            exist_config_file_path_replacement_string_before_replace = False
            exist_profile_name_replacement_string_before_replace = False
            exist_region_replacement_string_before_replace = False
            exist_output_replacement_string_before_replace = False
            exist_change_log_file_path_replacement_string_before_replace = False
            not_exist_config_file_path_before_replace = False
            not_exist_profile_name_before_replace = False
            not_exist_region_before_replace = False
            not_exist_output_before_replace = False
            not_exist_change_log_file_path_before_replace = False

            config = setup.load_setup_config(SETUP_CONFIG_FILE_PATH)
            config_file_path = config.config_file_path
            profile_name = config.profile_name
            region = config.region
            output = config.output
            change_log_file_path = config.change_log_file_path
            with open(template_file_path, "r") as f:
                before_template = f.read()
                if REPLACEMENT_STRING_CONFIG_FILE_PATH in before_template:
                    exist_config_file_path_replacement_string_before_replace = True
                if REPLACEMENT_STRING_REGISTER_PROFILE in before_template:
                    exist_profile_name_replacement_string_before_replace = True
                if REPLACEMENT_STRING_REGION_NAME in before_template:
                    exist_region_replacement_string_before_replace = True
                if REPLACEMENT_STRING_OUTPUT_FORMAT in before_template:
                    exist_output_replacement_string_before_replace = True
                if REPLACEMENT_STRING_CHANGE_LOG_FILE_PATH in before_template:
                    exist_change_log_file_path_replacement_string_before_replace = True
                if config_file_path not in before_template:
                    not_exist_config_file_path_before_replace = True
                if profile_name not in before_template:
                    not_exist_profile_name_before_replace = True
                if region not in before_template:
                    not_exist_region_before_replace = True
                if output not in before_template:
                    not_exist_output_before_replace = True
                if change_log_file_path not in before_template:
                    not_exist_change_log_file_path_before_replace = True

            ## when
            config = setup.load_setup_config(setup.SETUP_CONFIG_FILE_PATH)
            str_register_sts_assumed_role = setup.replace_replacement_string(
                before_template,
                config.config_file_path,
                config.profile_name,
                config.region,
                config.output,
                config.change_log_file_path,
            )

            ## then
            self.assertIn(config_file_path, str_register_sts_assumed_role)
            self.assertNotIn(
                REPLACEMENT_STRING_CONFIG_FILE_PATH, str_register_sts_assumed_role
            )
            self.assertIn(profile_name, str_register_sts_assumed_role)
            self.assertNotIn(
                REPLACEMENT_STRING_REGISTER_PROFILE, str_register_sts_assumed_role
            )
            self.assertIn(region, str_register_sts_assumed_role)
            self.assertNotIn(
                REPLACEMENT_STRING_REGION_NAME, str_register_sts_assumed_role
            )
            self.assertIn(output, str_register_sts_assumed_role)
            self.assertNotIn(
                REPLACEMENT_STRING_OUTPUT_FORMAT, str_register_sts_assumed_role
            )
            self.assertIn(change_log_file_path, str_register_sts_assumed_role)
            self.assertNotIn(
                REPLACEMENT_STRING_CHANGE_LOG_FILE_PATH, str_register_sts_assumed_role
            )
            self.assertTrue(exist_config_file_path_replacement_string_before_replace)
            self.assertTrue(exist_profile_name_replacement_string_before_replace)
            self.assertTrue(exist_region_replacement_string_before_replace)
            self.assertTrue(exist_output_replacement_string_before_replace)
            self.assertTrue(
                exist_change_log_file_path_replacement_string_before_replace
            )
            self.assertTrue(not_exist_config_file_path_before_replace)
            self.assertTrue(not_exist_profile_name_before_replace)
            self.assertTrue(not_exist_region_before_replace)
            self.assertTrue(not_exist_output_before_replace)
            self.assertTrue(not_exist_change_log_file_path_before_replace)

    def test_backup_file_success(self):
        ## given
        file_path = "test_backup_file_success.txt"
        test_string = "test"
        with open(file_path, "w") as test_file:
            test_file.write(test_string)

        now = datetime.datetime.now()

        ## when
        backup_file_path = setup.backup_file(file_path, now, logger)

        ## then
        self.assertTrue(os.path.exists(backup_file_path))
        self.assertEqual(
            backup_file_path, file_path + "_bk_" + now.strftime("%Y%m%d%H%M%S")
        )
        with open(backup_file_path, "r") as backup_file:
            self.assertEqual(backup_file.read(), test_string)
        os.remove(file_path)
        os.remove(backup_file_path)

    def test_backup_file_file_not_exist(self):
        ## given
        file_path = "test_backup_file_file_not_exist.txt"

        ## when
        backup_file_path = setup.backup_file(file_path, datetime.datetime.now(), logger)

        ## then
        self.assertIsNone(backup_file_path)

    def test_exist_register_sts_assumed_role_file_not_exist(self):
        ## given
        file_path = "test_exist_register_sts_assumed_role_file_not_exist.txt"

        ## when
        exist_register_sts_assumed_role = setup.exist_register_sts_assumed_role(
            file_path,
            setup.REGISTER_STS_ASSUMED_ROLE_START_SIGNAL,
            setup.REGISTER_STS_ASSUMED_ROLE_END_SIGNAL,
        )

        ## then
        self.assertFalse(exist_register_sts_assumed_role)

    def test_exist_register_sts_assumed_role_expected_value(self):
        ## given
        exist_signal_file_path = "exist_register_sts_assumed_role.rc"
        test_string = "test"
        with open(exist_signal_file_path, "w") as exist_signal_file:
            exist_signal_file.writelines(REGISTER_STS_ASSUMED_ROLE_START_SIGNAL + "\n")
            exist_signal_file.writelines(test_string + "\n")
            exist_signal_file.writelines(REGISTER_STS_ASSUMED_ROLE_END_SIGNAL)

        not_exist_signal_file_path = "not_exist_register_sts_assumed_role.rc"
        with open(not_exist_signal_file_path, "w") as not_exist_signal_file:
            not_exist_signal_file.write(test_string)

        exist_signal_but_wrong_order_file_path = (
            "wrong_order_register_sts_assumed_role.rc"
        )
        with open(exist_signal_but_wrong_order_file_path, "w") as wrong_order_file:
            wrong_order_file.writelines(REGISTER_STS_ASSUMED_ROLE_END_SIGNAL + "\n")
            wrong_order_file.writelines(test_string + "\n")
            wrong_order_file.writelines(REGISTER_STS_ASSUMED_ROLE_START_SIGNAL)

        login_shell_setting_file_paths = [
            {"file_path": exist_signal_file_path, "expected_value": True,},
            {"file_path": not_exist_signal_file_path, "expected_value": False,},
            {
                "file_path": exist_signal_but_wrong_order_file_path,
                "expected_value": False,
            },
        ]

        for login_shell_setting_file in login_shell_setting_file_paths:
            ## when
            exist_register_sts_assumed_role = setup.exist_register_sts_assumed_role(
                login_shell_setting_file["file_path"],
                setup.REGISTER_STS_ASSUMED_ROLE_START_SIGNAL,
                setup.REGISTER_STS_ASSUMED_ROLE_END_SIGNAL,
            )

            ## then
            self.assertEqual(
                exist_register_sts_assumed_role,
                login_shell_setting_file["expected_value"],
            )

        os.remove(exist_signal_file_path)
        os.remove(not_exist_signal_file_path)
        os.remove(exist_signal_but_wrong_order_file_path)

    def test_register_function_insert_success(self):
        login_shells = ["/bin/bash", "/usr/local/bin/zsh"]
        for login_shell in login_shells:
            ## given
            function_string = self.__generate_function_string(login_shell)
            insert_file_path = (
                "test_register_function"
                + login_shell.replace("/", "_")
                + "_insert_success.rc"
            )
            test_string = "test"
            with open(insert_file_path, "w") as insert_file:
                insert_file.write(test_string)

            ## when
            setup.register_function(function_string, insert_file_path, logger)

            ## then
            with open(insert_file_path, "r") as result_file:
                self.assertEqual(
                    result_file.read(), test_string + "\n" + function_string
                )

            os.remove(insert_file_path)

    def test_register_function_update_success(self):
        login_shells = ["/bin/bash", "/usr/local/bin/zsh"]
        for login_shell in login_shells:
            ## given
            function_string = self.__generate_function_string(login_shell)
            update_file_path = (
                "test_register_function"
                + login_shell.replace("/", "_")
                + "_update_success.rc"
            )
            test_replaced_string = "test_replaced_string"
            before_text = "before"
            after_text = "after"
            with open(update_file_path, "w") as update_file:
                update_file.writelines(before_text + "\n")
                update_file.writelines(REGISTER_STS_ASSUMED_ROLE_START_SIGNAL + "\n")
                update_file.writelines(test_replaced_string + "\n")
                update_file.writelines(REGISTER_STS_ASSUMED_ROLE_END_SIGNAL + "\n")
                update_file.writelines(after_text)

            ## when
            setup.register_function(function_string, update_file_path, logger)

            ## then
            with open(update_file_path, "r") as result_file:
                login_shell_setting = result_file.read()
                self.assertNotIn(login_shell_setting, test_replaced_string)
                self.assertEqual(
                    login_shell_setting,
                    before_text + "\n" + function_string + "\n" + after_text,
                )

            os.remove(update_file_path)

    def test_enabling_register_sts_assumed_role_success(self):
        login_shells = ["/bin/bash", "/usr/local/bin/zsh"]
        for login_shell in login_shells:
            ## given
            function_string = self.__generate_function_string(login_shell)
            test_string = "test"
            now = datetime.datetime.now()

            login_shell_setting_insert_file_path = (
                "test_enabling_register_sts_assumed_role_success"
                + login_shell.replace("/", "_")
                + "_insert.rc"
            )
            with open(
                login_shell_setting_insert_file_path, "w"
            ) as login_shell_setting_insert_file:
                login_shell_setting_insert_file.write(test_string)

            before_text = "before"
            after_text = "after"
            login_shell_setting_update_file_path = (
                "test_enabling_register_sts_assumed_role_success"
                + login_shell.replace("/", "_")
                + "_update.rc"
            )
            update_before_text = (
                before_text
                + "\n"
                + REGISTER_STS_ASSUMED_ROLE_START_SIGNAL
                + "\n"
                + test_string
                + "\n"
                + REGISTER_STS_ASSUMED_ROLE_END_SIGNAL
                + "\n"
                + after_text
            )
            with open(
                login_shell_setting_update_file_path, "w"
            ) as login_shell_setting_update_file:
                login_shell_setting_update_file.write(update_before_text)

            login_shell_settings = [
                {
                    "login_shell_settig_file_path": login_shell_setting_insert_file_path,
                    "before_expected_value": test_string,
                    "after_expected_value": test_string + "\n" + function_string,
                },
                {
                    "login_shell_settig_file_path": login_shell_setting_update_file_path,
                    "before_expected_value": update_before_text,
                    "after_expected_value": before_text
                    + "\n"
                    + function_string
                    + "\n"
                    + after_text,
                },
            ]

            for login_shell_setting in login_shell_settings:
                ## when
                login_shell_setting_file_path = login_shell_setting[
                    "login_shell_settig_file_path"
                ]
                setup.enabling_register_sts_assumed_role(
                    function_string, login_shell_setting_file_path, now, logger
                )

                ## then
                backup_file_path = (
                    login_shell_setting_file_path
                    + "_bk_"
                    + now.strftime("%Y%m%d%H%M%S")
                )
                self.assertTrue(os.path.exists(backup_file_path))
                with open(backup_file_path, "r") as backup_file:
                    self.assertEqual(
                        backup_file.read(), login_shell_setting["before_expected_value"]
                    )
                with open(login_shell_setting_file_path, "r") as result_file:
                    self.assertEqual(
                        result_file.read(), login_shell_setting["after_expected_value"]
                    )

                os.remove(login_shell_setting_file_path)
                os.remove(backup_file_path)

    def test_setup_register_sts_assumed_role_success(self):
        ## given
        now = datetime.datetime.now()
        if "SHELL" in os.environ:
            before_shell_environ = os.environ["SHELL"]
        os.environ["SHELL"] = "test"
        test_replaced_string = "test_replaced_string"
        before_text = "before"
        after_text = "after"
        login_shell_setting_file_path = "test_login_shell_setting_file_path.rc"
        with open(login_shell_setting_file_path, "w") as test_login_shell_setting_file:
            test_login_shell_setting_file.writelines(before_text + "\n")
            test_login_shell_setting_file.writelines(
                REGISTER_STS_ASSUMED_ROLE_START_SIGNAL + "\n"
            )
            test_login_shell_setting_file.writelines(test_replaced_string + "\n")
            test_login_shell_setting_file.writelines(
                REGISTER_STS_ASSUMED_ROLE_END_SIGNAL + "\n"
            )
            test_login_shell_setting_file.writelines(after_text)
        tmp_stdout, sys.stdout = sys.stdout, StringIO()

        ## when
        setup.setup_register_sts_assumed_role(
            setup.load_setup_config(setup.SETUP_CONFIG_FILE_PATH), now, logger
        )

        ## then
        self.assertEqual(
            sys.stdout.getvalue(),
            "Setup successed. please run `source "
            + login_shell_setting_file_path
            + "` command.\n",
        )
        backup_file_path = (
            login_shell_setting_file_path + "_bk_" + now.strftime("%Y%m%d%H%M%S")
        )
        self.assertTrue(os.path.exists(backup_file_path))
        with open(backup_file_path, "r") as backup_file:
            self.assertEqual(
                backup_file.read(),
                before_text
                + "\n"
                + REGISTER_STS_ASSUMED_ROLE_START_SIGNAL
                + "\n"
                + test_replaced_string
                + "\n"
                + REGISTER_STS_ASSUMED_ROLE_END_SIGNAL
                + "\n"
                + after_text,
            )

        function_string = setup.generate_register_sts_assumed_role_template(
            REGISTER_STS_ASSUMED_ROLE_BASH_TEMPLATE_FILE_PATH,
            setup.load_setup_config(SETUP_CONFIG_FILE_PATH),
        )
        with open(login_shell_setting_file_path, "r") as result_file:
            login_shell_setting = result_file.read()
            self.assertNotIn(login_shell_setting, test_replaced_string)
            self.assertEqual(
                login_shell_setting,
                before_text + "\n" + function_string + "\n" + after_text,
            )

        sys.stdout = tmp_stdout
        if "before_shell_environ" in locals():
            os.environ["SHELL"] = before_shell_environ
        os.remove(login_shell_setting_file_path)
        os.remove(backup_file_path)

    def test_setup_register_sts_assumed_role_login_shell_not_found(self):
        ## given
        now = datetime.datetime.now()
        if "SHELL" in os.environ:
            before_shell_environ = os.environ["SHELL"]
            del os.environ["SHELL"]
        tmp_stdout, sys.stdout = sys.stdout, StringIO()

        ## when
        setup.setup_register_sts_assumed_role(
            setup.load_setup_config(setup.SETUP_CONFIG_FILE_PATH), now, logger
        )

        ## then
        self.assertEqual(
            sys.stdout.getvalue(), "Login shells not found.\n",
        )

        sys.stdout = tmp_stdout
        if "before_shell_environ" in locals():
            os.environ["SHELL"] = before_shell_environ

    def test_setup_register_sts_assumed_role_login_shell_not_supported(self):
        ## given
        now = datetime.datetime.now()
        if "SHELL" in os.environ:
            before_shell_environ = os.environ["SHELL"]
        os.environ["SHELL"] = "not_supported"
        tmp_stdout, sys.stdout = sys.stdout, StringIO()

        ## when
        setup.setup_register_sts_assumed_role(
            setup.load_setup_config(setup.SETUP_CONFIG_FILE_PATH), now, logger
        )

        ## then
        self.assertEqual(
            sys.stdout.getvalue(),
            "Sorry. the only supported login shells are bash and zsh.\n",
        )

        sys.stdout = tmp_stdout
        if "before_shell_environ" in locals():
            os.environ["SHELL"] = before_shell_environ

    ####################################
    ########## Private Method ##########
    ####################################
    def __generate_function_string(self, login_shell_path):
        if login_shell_path.endswith("bash"):
            template_file_path = REGISTER_STS_ASSUMED_ROLE_BASH_TEMPLATE_FILE_PATH
        elif login_shell_path.endswith("zsh"):
            template_file_path = REGISTER_STS_ASSUMED_ROLE_ZSH_TEMPLATE_FILE_PATH
        return setup.generate_register_sts_assumed_role_template(
            template_file_path, setup.load_setup_config(SETUP_CONFIG_FILE_PATH),
        )

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == "__main__":
    unittest.main()
