import yaml
import logging
import os
import datetime
import shutil

## const value
SETUP_CONFIG_FILE_PATH = "config/setup-config.yaml"
SETUP_LOG_FILE_PATH = "logs/setup.log"
BASH_LOGIN_SHELL_SETTING_FILE_PATH = "$HOME/.bashrc"
ZSH_LOGIN_SHELL_SETTING_FILE_PATH = "$HOME/.zshrc"
REGISTER_STS_ASSUMED_ROLE_TEMPLATE_FILE_PATH = "template/register_sts_assumed_role.tmpl"
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


class SetupConfigVO:
    def __init__(
        self, config_file_path, profile_name, region, output, change_log_file_path
    ):
        """
        Parameters
        ----------
        config_file_path : str
            AWS CLI config file path.
        profile_name : str
            default profile name.
        region : str
            default region name.
        output : str
            default output format.
        change_log_file_path : str
            file path for config file change log.
        """
        self.config_file_path = config_file_path
        self.profile_name = profile_name
        self.region = region
        self.output = output
        self.change_log_file_path = change_log_file_path


def load_setup_config(yaml_file_path):
    """
    Load setup config from yaml file.

    Parameters
    ----------
    yaml_file_path : str
        setup-config yaml file path.

    Returns
    -------
    setup_config : SetupConfigVO
        loaded config detail value object.
    """
    with open(yaml_file_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)["setup"]

    register_profile = config["register_profile"]
    return SetupConfigVO(
        config["config_file"]["file_path"],
        register_profile["profile_name"]["default"],
        register_profile["region"]["default"],
        register_profile["output"]["default"],
        config["change_log"]["file_path"],
    )


def initialize_logger_setting():
    """
    Initialize logger setting.

    Returns
    -------
    logger : logger
        logging.logger object.
    """
    if not os.path.isdir("logs"):
        os.makedirs("logs")
    logging.basicConfig(filename=SETUP_LOG_FILE_PATH)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


def get_login_shell_setting_file_path(login_shell_path):
    """
    Get your local login shell setting file path.

    Parameters
    ----------
    login_shell_path : str
        Your local login shell path.

    Returns
    -------
    login_shell_setting_file_path : str
        login shell setting file path.
    """
    if login_shell_path is None:
        return None
    elif login_shell_path.endswith("bash"):
        return BASH_LOGIN_SHELL_SETTING_FILE_PATH.replace("$HOME", os.environ["HOME"])
    elif login_shell_path.endswith("zsh"):
        return ZSH_LOGIN_SHELL_SETTING_FILE_PATH.replace("$HOME", os.environ["HOME"])
    else:
        return None


def replace_replacement_string(
    template_string,
    config_file_path,
    profile_name,
    region,
    output,
    change_log_file_path,
):
    """
    Generate register-sts-assumed-role function string.

    Parameters
    ----------
    template_string : str
        register-sts-assumed-role function template string.
    config_file_path : str
        AWS CLI config file path.
    profile_name : str
        default profile name.
    region : str
        default region name.
    output : str
        default output format.
    change_log_file_path : str
        file path for config file change log.

    Returns
    -------
    str_register_sts_assumed_role : str
        register-sts-assumed-role function string.
    """
    return (
        template_string.replace(REPLACEMENT_STRING_CONFIG_FILE_PATH, config_file_path)
        .replace(REPLACEMENT_STRING_REGISTER_PROFILE, profile_name)
        .replace(REPLACEMENT_STRING_REGION_NAME, region)
        .replace(REPLACEMENT_STRING_OUTPUT_FORMAT, output)
        .replace(REPLACEMENT_STRING_CHANGE_LOG_FILE_PATH, change_log_file_path)
    )


def generate_register_sts_assumed_role_template(template_file_path, setup_config):
    """
    Generate register-sts-assumed-role function string.

    Parameters
    ----------
    template_file_path : str
        register-sts-assumed-role template file path.
    setup_config : SetupConfigVO
        loaded config detail value object.

    Returns
    -------
    function_string : str
        register-sts-assumed-role function string.
    """
    with open(template_file_path, "r") as f:
        return replace_replacement_string(
            f.read(),
            setup_config.config_file_path,
            setup_config.profile_name,
            setup_config.region,
            setup_config.output,
            setup_config.change_log_file_path,
        )


def backup_file(file_path, logger):
    """
    Backup login shell setting file before change.

    Parameters
    ----------
    file_path : str
        backup target file path.
    logger : logger
        logging.logger object.

    Returns
    -------
    backup_file_path : str
        backup result file path.
    """
    if os.path.exists(file_path) == False:
        logger.warn(
            datetime.datetime.now().isoformat()
            + " backup target file not exist. file_path: "
            + file_path
        )
        return None
    backup_file_path = (
        file_path + "_bk_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    )
    shutil.copy(file_path, backup_file_path)
    logger.info(
        datetime.datetime.now().isoformat()
        + " backup file success. file_path: "
        + file_path
        + ", backup_file_path: "
        + backup_file_path
    )
    return backup_file_path


def reload_login_shell_setting_file(login_shell_setting_file_path):
    """
    Run the source of linux commands in the login shell setting file.

    Parameters
    ----------
    login_shell_setting_file_path : str
        login shell setting file path.
    """
    pass


def enabling_register_sts_assumed_role(
    function_string, login_shell_setting_file_path, logger
):
    """
    Register register_sts_assumed_role function to login shell setting file.

    Parameters
    ----------
    function_string : str
        register-sts-assumed-role function string.
    login_shell_setting_file_path : str
        login shell setting file path.
    logger : logger
        logging.logger object.
    """
    backup_file(login_shell_setting_file_path, logger)
    reload_login_shell_setting_file(login_shell_setting_file_path)


def setup_register_sts_assumed_role(setup_config, logger):
    """
    Setup register_sts_assumed_role function to login shell setting file.

    Parameters
    ----------
    setup_config : SetupConfigVO
        loaded config detail value object.
    logger : logger
        logging.logger object.
    """
    login_shell_path = os.environ["SHELL"]
    login_shell_setting_file_path = get_login_shell_setting_file_path(login_shell_path)
    if login_shell_setting_file_path is None:
        logger.error(
            datetime.datetime.now().isoformat()
            + " Login shell not supported error. login_shell_path = "
            + login_shell_path
        )
        print("Sorry. the only supported login shells are bash and zsh.")
        return

    enabling_register_sts_assumed_role(
        generate_register_sts_assumed_role_template(
            REGISTER_STS_ASSUMED_ROLE_TEMPLATE_FILE_PATH, setup_config
        ),
        login_shell_setting_file_path,
        logger,
    )

    logger.info(
        datetime.datetime.now().isoformat()
        + "execute setup_register_sts_assumed_role successed."
    )
    print("setup successed.")


if __name__ == "__main__":
    config = load_setup_config(SETUP_CONFIG_FILE_PATH)
    setup_register_sts_assumed_role(
        config, initialize_logger_setting(),
    )
