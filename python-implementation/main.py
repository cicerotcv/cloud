# -*- encoding utf-8 -*-
from time import sleep

from dotenv import dotenv_values

from controller.filesystem import filesystem as fs
from controller.session import Session
from controller.utils import print_status, print_public_ip, replace
from controller.context_manager import ContextManager
from controller.logger import logger


def create_ohio(session: Session, credentials):
    ohio = session.load_region('ohio')
    ohio.wipe()

    o_kp = ohio.key_pair
    o_kp.create()

    o_sg = ohio.security_group
    o_sg.enable_ingress('ssh', 'http', 'mongodb')
    o_sg.enable_egress('http', 'software_update')
    o_sg.create()

    o_instances = ohio.init_client('ohio-database')
    db_statup_script = replace(fs.read('setup_database.sh'), credentials)

    database = ohio.create_instance(db_statup_script)
    o_instances.wait_until_running(InstanceIds=[database.InstanceId])
    o_instances.refresh()

    print_public_ip(database)
    return database.PublicIpAddress


def create_north_virginia(session, credentials, database_host):
    # carregar região "North Virginia"
    n_virginia = session.load_region('n_virginia')
    n_virginia.wipe()

    # criar key pair em north virginia
    nv_kp = n_virginia.key_pair
    nv_kp.create()

    # criar security group em north virginia
    nv_sg = n_virginia.security_group
    nv_sg.enable_ingress('ssh', 'http')
    nv_sg.enable_egress('http', 'software_update')
    nv_sg.create()

    # iniciliazar o gerenciador de instancias de North Virginia
    nv_instances = n_virginia.init_client('nv-webserver')

    # configurar programa de inicialização de North Virginia (UserData)
    ws_credentials = {
        **credentials,
        "MONGO_HOST": database_host  # ohio_instance.PublicIp
    }
    ws_initializer = replace(fs.read('setup_server.sh'), ws_credentials)

    # criar instancia em NV
    webserver = n_virginia.create_instance(ws_initializer, wait=True)

    nv_instances.refresh()
    print_public_ip(webserver)

    # criar uma AMI de north virginia
    nv_ami = n_virginia.images.create(webserver.InstanceId, 'nv-ami')
    nv_instances.terminate_instances([webserver.InstanceId], wait=True)

    # criar load balancer + autoscaling
    # logger.log("Creating launch configuration")
    nv_lc = n_virginia.launch_configuration
    nv_lc.create_from_instance(webserver, nv_ami,
                               nv_sg.GroupId, UserData=ws_initializer)

    nv_lb = n_virginia.load_balancer
    subnet_ids = n_virginia.get_subnets()
    nv_lb.create(groupIds=[nv_sg.GroupId], subnet_ids=subnet_ids)
    tg_arn = nv_lb.target_group.ARN

    # criar auto scaling group
    nv_as = n_virginia.auto_scaling
    nv_as.create_auto_scalling(nv_lc.name, tg_arn, min_size=1)


if __name__ == "__main__":
    with ContextManager() as session:
        credentials = dotenv_values()

        database_host = create_ohio(session, credentials)

        create_north_virginia(session, credentials, database_host)

        logger.log("Waiting for interruption...")
        while True:
            sleep(30)
