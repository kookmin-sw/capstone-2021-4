from project import app,db
from project.models import Oslist, Plan

sample_plan = Plan('m1.small', 't3.small', 1, 1024, 1, 40, 4000)
db.session.add(sample_plan)

sample_os = Oslist('ubuntu20.04', 'ami-067abcae434ee508b')
sample_os2  = Oslist('amazonLinux', 'ami-09282971cf2faa4c9')

db.session.add(sample_os)
db.session.add(sample_os2)

db.session.commit()
