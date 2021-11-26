# -*- encoding utf-8 -*-
from time import sleep

from dotenv import dotenv_values

from controller.filesystem import filesystem as fs
from controller.utils import print_status, print_public_ip, replace
from controller.context_manager import ContextManager


if __name__ == "__main__":
    with ContextManager() as session:
        credentials = dotenv_values()

        ohio = session.load_region('ohio')

        o_kp = ohio.create_key_pair('o-kp')
        o_sg = ohio.init_security_group('o-sg', "::Ohio::")

        o_sg.enable_ingress('ssh', 'http', 'mongodb')
        o_sg.enable_egress('http', 'software_update')
        o_sg.create()

        ohio_manager = ohio.init_client('ohio')

        db_initializer = replace(fs.read('setup_database.sh'), credentials)

        database = ohio.create_instance(db_initializer)

        # n_virginia = session.load_region('n_virginia')

        # # creating key pair
        # nv_kp = n_virginia.create_key_pair('nv-kp')

        # # creating security group in North Virginia
        # nv_sg = n_virginia.init_security_group("nv-sg", "::North Virginia::")
        # nv_sg.enable_ingress('ssh', 'http')
        # nv_sg.enable_egress('http', 'software_update')
        # nv_sg.create()

        # north_virginia = n_virginia.init_client('north-virginia')
        # ws_initializer = replace(fs.read('setup_server.sh'), credentials)

        # webserver = n_virginia.create_instance(ws_initializer)

        # # north_virginia.create_image(webserver.InstanceId, "ami-webserver")

        # north_virginia.wait_until_running(InstanceIds=[webserver.InstanceId])
        ohio_manager.wait_until_running(InstanceIds=[database.InstanceId])

        ohio_manager.refresh()
        # north_virginia.refresh()

        while True:
            instances = ohio.get_instances() 
            # + n_virginia.get_instances()
            for instance in instances:
                print_status(instance)
                print_public_ip(instance)
            sleep(30)
