
class User:
    def __init__(self, user, uid):
        self.user = user
        self.uid = uid
        #super().__init__()

    def __init__(self):
        self.user = None
        self.uid = None

    def _getUser_(self):
        return self.user

    def _setUser_(self, user):
        self.user = user

    def _setUser_Id_(self, uid):
        self.uid = uid

    def _getUser_Id_(self):
        return self.uid

    def _getUser_email(self):
        return self.user["email"]

    def _getUser_name(self):
        return self.user["name"]

    def _getUser_username(self):
        return self.user["username"]

    def _getUser_image(self):
        return self.user["image"]

    def _getUser_joined_date(self):
        return self.user["joined"]

    def _getUser_bio(self):
        return self.user["bio"]     

    def _isNone_(self):
        if self.user is None and self.uid is None:
            return True
        return False                               