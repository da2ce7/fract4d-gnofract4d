from datetime import datetime
from turbogears.database import PackageHub
from sqlobject import *
from turbogears import identity 

hub = PackageHub("elephant_valley")
__connection__ = hub

# identity models.
class Visit(SQLObject):
    class sqlmeta:
        table = "visit"

    visit_key = StringCol(length=40, alternateID=True,
                          alternateMethodName="by_visit_key")
    created = DateTimeCol(default=datetime.now)
    expiry = DateTimeCol()

    def lookup_visit(cls, visit_key):
        try:
            return cls.by_visit_key(visit_key)
        except SQLObjectNotFound:
            return None
    lookup_visit = classmethod(lookup_visit)

class VisitIdentity(SQLObject):
    visit_key = StringCol(length=40, alternateID=True,
                          alternateMethodName="by_visit_key")
    user_id = IntCol()


class Group(SQLObject):
    """
    An ultra-simple group definition.
    """

    # names like "Group", "Order" and "User" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table = "tg_group"

    group_name = UnicodeCol(length=16, alternateID=True,
                            alternateMethodName="by_group_name")
    display_name = UnicodeCol(length=255)
    created = DateTimeCol(default=datetime.now)

    # collection of all users belonging to this group
    users = RelatedJoin("User", intermediateTable="user_group",
                        joinColumn="group_id", otherColumn="user_id")

    # collection of all permissions for this group
    permissions = RelatedJoin("Permission", joinColumn="group_id", 
                              intermediateTable="group_permission",
                              otherColumn="permission_id")


class User(SQLObject):
    """
    Reasonably basic User definition. Probably would want additional attributes.
    """
    # names like "Group", "Order" and "User" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table = "tg_user"

    user_name = UnicodeCol(length=16, alternateID=True,
                           alternateMethodName="by_user_name")
    email_address = UnicodeCol(length=255, alternateID=True,
                               alternateMethodName="by_email_address")
    display_name = UnicodeCol(length=255)
    password = UnicodeCol(length=40)
    created = DateTimeCol(default=datetime.now)

    # groups this user belongs to
    groups = RelatedJoin("Group", intermediateTable="user_group",
                         joinColumn="user_id", otherColumn="group_id")

    def _get_permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    def _set_password(self, cleartext_password):
        "Runs cleartext_password through the hash algorithm before saving."
        hash = identity.encrypt_password(cleartext_password)
        self._SO_set_password(hash)

    def set_password_raw(self, password):
        "Saves the password as-is to the database."
        self._SO_set_password(password)



class Permission(SQLObject):
    permission_name = UnicodeCol(length=16, alternateID=True,
                                 alternateMethodName="by_permission_name")
    description = UnicodeCol(length=255)

    groups = RelatedJoin("Group",
                        intermediateTable="group_permission",
                         joinColumn="permission_id", 
                         otherColumn="group_id")


class FormulaFile(SQLObject):
    file_name = StringCol(alternateID=True)
    formulas = MultipleJoin('Formula')
    owner = ForeignKey('User')
    
class Formula(SQLObject):
    formula_name = StringCol()
    formulaFile = ForeignKey('FormulaFile')
    fractals = RelatedJoin('Fractal')
    
class Fractal(SQLObject):
    title = StringCol()
    description = StringCol()
    formulas = RelatedJoin('Formula')
    owner = ForeignKey('User')

def ensureTables():
    for t in [Fractal, Formula, FormulaFile,
              User, Group, Permission, Visit, VisitIdentity]:
        t.dropTable(ifExists=True)
        t.createTable(ifNotExists=False)

def addTestData():
    
    for user in User.selectBy(email_address=u"fred@elephantvalley.net"):
        print user
        user.destroySelf()

    uid = u"fred@elephantvalley.net"
    user = User(
        user_name=u"fred",
        email_address=uid,
        display_name=u"Freddikins",
        password=u"spigot")

    uid2 = u"bert@evil.com"
    user = User(
        user_name=u"bert",
        email_address=uid2,
        display_name=u"Evil Bert",
        password=u"malice")
    
    formulafiles = [
        FormulaFile(file_name = "gf4d.frm", ownerID=uid),
        FormulaFile(file_name = "gf4d.cfrm", ownerID=uid),
        FormulaFile(file_name = "gf4d.uxf", ownerID=uid),
        FormulaFile(file_name = "bert.frm", ownerID=uid2)
    ]

    ff = formulafiles[0]
    formulas = [
        Formula(formulaFile=ff,formula_name="Mandelbrot"),
        Formula(formulaFile=ff,formula_name="Julia"),
        Formula(formulaFile=formulafiles[3],formula_name="Bert's Formula")
    ]

    f1 = Fractal(title="a",description="wibble",ownerID=uid)
    f1.addFormula(formulas[0])
    f2 = Fractal(title="b",description="wibble2",ownerID=uid)
    f2.addFormula(formulas[1])
    f3 = Fractal(title="bert's fractal",description="A fractal by bert", ownerID=uid2)
