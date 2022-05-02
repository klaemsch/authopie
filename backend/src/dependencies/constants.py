class Scope:
    """
    Class for comparing required Scopes against scopes in a token
    Is required to allow setting aliases as shown below:
    the scope 'manage-users' should be included in '*'
    """

    def __init__(self, *args):
        self.scopes = list(args)

    def __contains__(self, user_scopes: list[str]) -> bool:
        """
        compares given user scopes from JWT (user has those)
        with scopes of this instance (user needs one of those)
        """

        # user has user_scopes
        # user needs one of self.scopes

        # compare
        for user_scope in user_scopes:
            if user_scope in self.scopes:
                # found a scope the user has in common with this instance
                return True

        # no scope of the user satisfied those in this instance
        return False

    def __str__(self) -> str:
        return str(self.scopes)

    def __repr__(self) -> str:
        return self.__str__()


class Scopes:
    """
    All scopes that are internally used
    """
    GOD = Scope('*')
    MANAGE_USERS = Scope('manage-users', '*')
    MANAGE_ROLES = Scope('manage-roles', '*')
