from logging import error, exception, warning, debug


def msg(m: str) -> None:
    print(f"<MSG---[{m}]-->")


def exc(e: Exception, msg:str = "") -> None:
    exception(f"<EXC---[Exception: {str(e)}]--->")
    if msg != "":
        err(f"{msg}")
    #print(traceback.format_exc())


def err(m: str) -> None:
    error(f"<ERR---[{m}]-->")


def deb(m: str) -> None:
    debug(f"<DEBUG---[{m}]-->")


def warn(m: str) -> None:
    warning(f"<WARNING---[{m}]-->")
