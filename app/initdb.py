from project import app,db
from project.models import Oslist, Plan
#plan
# id: int
# plan_name: str
# aws_plan: str
# core: int
# ram: int
# traffic:int
# ssd: int
# iops: int
# sample_plan = Plan('m2.small', 't3.small', 1, 2048, 2000, 40, 4000)
sample_plan2 = Plan('m3.medium', 't3.medium	', 4096, 4000, 2048, 60, 4500)
sample_plan3 = Plan('m3.big', 't3.xlarge', 4, 16384, 6000, 100, 5000)
sample_plan4 = Plan('m4.large', 't3.2xlarge', 8, 32768, 8000, 100, 5500)
db.session.add(sample_plan2)
db.session.add(sample_plan3)
db.session.add(sample_plan4)

# sample_os = Oslist('ubuntu20.04', 'ami-067abcae434ee508b')
# sample_os2  = Oslist('amazonLinux', 'ami-09282971cf2faa4c9')

# db.session.add(sample_os)
# db.session.add(sample_os2)

db.session.commit()
