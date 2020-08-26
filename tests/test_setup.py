import unittest
import setup
import logging
import os
import yaml

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
REGISTER_STS_ASSUMED_ROLE_TEMPLATE_FILE_PATH = "template/register_sts_assumed_role.tmpl"
REPLACEMENT_STRING_CONFIG_FILE_PATH = "$REPLACEMENT_STRING_CONFIG_FILE_PATH"
REPLACEMENT_STRING_REGISTER_PROFILE = "$REPLACEMENT_STRING_REGISTER_PROFILE"
REPLACEMENT_STRING_REGION_NAME = "$REPLACEMENT_STRING_REGION_NAME"
REPLACEMENT_STRING_OUTPUT_FORMAT = "$REPLACEMENT_STRING_OUTPUT_FORMAT"
REPLACEMENT_STRING_CHANGE_LOG_FILE_PATH = "$REPLACEMENT_STRING_CHANGE_LOG_FILE_PATH"


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

    def test_generate_register_sts_assumed_role_template_expected_value(self):
        ## given
        with open(REGISTER_STS_ASSUMED_ROLE_TEMPLATE_FILE_PATH) as template_file:
            expected_value = (
                template_file.read()
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
        str_register_sts_assumed_role = setup.generate_register_sts_assumed_role_template(
            setup.REGISTER_STS_ASSUMED_ROLE_TEMPLATE_FILE_PATH,
            setup.load_setup_config(setup.SETUP_CONFIG_FILE_PATH),
        )

        ## then
        self.assertEqual(str_register_sts_assumed_role, expected_value)

    def test_replace_replacement_string(self):
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

        config = setup.load_setup_config(setup.SETUP_CONFIG_FILE_PATH)
        config_file_path = config.config_file_path
        profile_name = config.profile_name
        region = config.region
        output = config.output
        change_log_file_path = config.change_log_file_path
        with open(setup.REGISTER_STS_ASSUMED_ROLE_TEMPLATE_FILE_PATH, "r") as f:
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
        str_register_sts_assumed_role = setup.replace_replacement_string(
            before_template,
            config_file_path,
            profile_name,
            region,
            output,
            change_log_file_path,
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
        self.assertNotIn(REPLACEMENT_STRING_REGION_NAME, str_register_sts_assumed_role)
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
        self.assertTrue(exist_change_log_file_path_replacement_string_before_replace)
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

        ## when
        backup_file_path = setup.backup_file(file_path, logger)

        ## then
        self.assertTrue(os.path.exists(backup_file_path))
        with open(backup_file_path) as backup_file:
            self.assertEqual(backup_file.read(), test_string)
        os.remove(file_path)
        os.remove(backup_file_path)

    def test_backup_file_file_not_exist(self):
        ## given
        file_path = "test_backup_file_file_not_exist.txt"

        ## when
        backup_file_path = setup.backup_file(file_path, logger)

        ## then
        self.assertIsNone(backup_file_path)

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == "__main__":
    unittest.main()
