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

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == "__main__":
    unittest.main()
