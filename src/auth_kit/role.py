from enum import StrEnum


class Role(StrEnum):
    ADMINISTRATOR = "administrator"
    USAGER = "usager"

    def is_administrator(self) -> bool:
        return self is Role.ADMINISTRATOR
