from enum import StrEnum


class Role(StrEnum):
    """Rôles applicatifs exposés par auth-kit.

    Trois niveaux (EPIC-013 / US-049) :

    * ``usager`` — agrégats ; pas de données nominatives ;
    * ``analyste_nominatif`` — données nominatives sans administration des comptes ;
    * ``administrator`` — seul rôle autorisé à gérer les utilisateurs.
    """

    ADMINISTRATOR = "administrator"
    ANALYSTE_NOMINATIF = "analyste_nominatif"
    USAGER = "usager"

    def is_administrator(self) -> bool:
        return self is Role.ADMINISTRATOR

    def is_analyste_nominatif(self) -> bool:
        return self is Role.ANALYSTE_NOMINATIF
