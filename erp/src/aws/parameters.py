from troposphere import Parameter

from magicdict import MagicDict


class Parameters(MagicDict):
    def __init__(self):
        super(Parameters, self).__init__()

        self.rdp_server_key_pair = Parameter(
            "RdpServerKeyPair",
            Type="AWS::EC2::KeyPair::KeyName",
            Description="Key pair to use to login to your Rdp server"
        )

        self.mssql_key_pair = Parameter(
            "MSSqlKeyPair",
            Type="AWS::EC2::KeyPair::KeyName",
            Description="Key pair to use to login to your mssql server"
        )

        self.app_server_key_pair = Parameter(
            "AppServerKeyPair",
            Type="AWS::EC2::KeyPair::KeyName",
            Description="Key pair to use to login to your app server"
        )

        self.web_server_key_pair = Parameter(
            "WebServerKeyPair",
            Type="AWS::EC2::KeyPair::KeyName",
            Description="Key pair to use to login to your web server"
        )

        # self.db_password = Parameter(
        #     "DBPassword",
        #     Type="String",
        #     NoEcho=True,
        #     MinLength=8,
        #     Description="Choose a secure password for your database with at least 1 small letter, 1 large letter, 1 number, minimal length: 8 characters.",
        #     AllowedPattern="^(?=.*[A-Z])(?=.*[0-9])(?=.*[a-z]).{8,}$",
        #     ConstraintDescription="Database password must be at least 8 characters, with 1 small letter, 1 large letter and 1 number. "
        # )

        # self.db_instance_type = Parameter(
        #     "DBInstanceType",
        #     Type="String",
        #     AllowedValues=[
        #         "db.t2.micro", "db.t2.small", "db.t2.medium", "db.t2.large",
        #         "db.m4.large", "db.m4.xlarge", "db.m4.2xlarge", "db.m4.4xlarge", "db.m4.10xlarge"
        #     ],
        #     Default="db.t2.micro",
        #     Description="Instance class for your database. Defines amount of CPU and Memory."
        # )

        # self.db_backup_retention = Parameter(
        #     "DBBackupRetention",
        #     Type="Number",
        #     Default="7",
        #     Description="Number of days to store automated daily database backups for."
        # )

        self.pro_rdp_server_ec2_instance_type = Parameter(
            "ProRdpServerEC2InstanceType",
            Type="String",
            AllowedValues=[
                "c3.large",
                "c3.xlarge",
                "c3.2xlarge",
                "c3.4xlarge",
                "c4.large",
                "c4.xlarge",
                "c4.2xlarge",
                "c4.4xlarge",
            ],
            Default="c3.xlarge",
            Description="Instance class for Pro rdp server. Defines amount of CPU and Memory."
        )

        self.ue_rdp_server_ec2_instance_type = Parameter(
            "UeRdpServerEC2InstanceType",
            Type="String",
            AllowedValues=[
                "c3.large",
                "c3.xlarge",
                "c3.2xlarge",
                "c3.4xlarge",
                "c4.large",
                "c4.xlarge",
                "c4.2xlarge",
                "c4.4xlarge",
            ],
            Default="c3.xlarge",
            Description="Instance class for UE rdp server. Defines amount of CPU and Memory."
        )

        self.sm_rdp_server_ec2_instance_type = Parameter(
            "SmRdpServerEC2InstanceType",
            Type="String",
            AllowedValues=[
                "c3.large",
                "c3.xlarge",
                "c3.2xlarge",
                "c3.4xlarge",
                "c4.large",
                "c4.xlarge",
                "c4.2xlarge",
                "c4.4xlarge",
            ],
            Default="c3.xlarge",
            Description="Instance class for SM rdp server. Defines amount of CPU and Memory."
        )

        self.app_server_ec2_instance_type = Parameter(
            "AppServerEC2InstanceType",
            Type="String",
            AllowedValues=[
                "m3.large",
                "m3.xlarge",
                "m3.2xlarge",
                "m3.4xlarge"
            ],
            Default="m3.large",
            Description="Instance class for app server. Defines amount of CPU and Memory."
        )

        self.web_server_ec2_instance_type = Parameter(
            "WebServerEC2InstanceType",
            Type="String",
            AllowedValues=[
                "m4.large",
                "m4.xlarge",
                "m4.2xlarge",
                "m4.4xlarge"
            ],
            Default="m4.large",
            Description="Instance class for Web server. Defines amount of CPU and Memory."
        )

        self.mssql_server_ec2_instance_type = Parameter(
            "MssqlEc2InstanceType",
            Type="String",
            AllowedValues=[
                "r4.large",
                "r4.xlarge",
                "r4.2xlarge",
                "r4.4xlarge",
                "r4.8xlarge"
            ],
            Default="r4.large",
            Description="Instance class for rdp server. Defines amount of CPU and Memory."
        )


        self.app_api_port = Parameter(
            "ApiServerPort",
            Type="String",
            Default="80",
            Description="TCP/IP port of the api server",
        )

        self.web_port = Parameter(
            "webServerPort",
            Type="String",
            Default="8088",
            Description="TCP/IP port of the web server",
        )

        # self.WebServerPort = Parameter(
        #     "WebServerPort",
        #     Type="String",
        #     Default="80",
        #     Description="TCP/IP port of the web server",
        # )

        # self.ECSImageId = Parameter(
        #     "ECSImageId",
        #     Type="String",
        #     Default="ami-087cfa08153018a91"
        # )

        self.MssqlServerImageId = Parameter(
            "MssqlServerImageId",
            Type="String",
            Default="ami-02cd86d8309ab34dd"
        )

        
        self.ProRdpServerImageId = Parameter(
            "ProRdpServerImageId",
            Type="String",
            Default="ami-076e3388927cd05f8"
        )

        self.SMRdpServerImageId = Parameter(
            "SMRdpServerImageId",
            Type="String",
            Default="ami-0798ef0fdc4e67d1b"
        )

        self.UERdpServerImageId = Parameter(
            "UERdpServerImageId",
            Type="String",
            Default="ami-027ea09961956c414"
        )

        

        self.WebPortalServerImageId = Parameter(
            "WebPortalServerImageId",
            Type="String",
            Default="ami-0fb9d02d706b826c2"
        )

        self.AppServerImageId = Parameter(
            "AppServerImageId",
            Type="String",
            Default="ami-0c54030c708a20120"
        )

        self.ScaleCapacity = Parameter(
            "ScaleCapacity",
            Default="1",
            Type="String",
            Description="Number of servers to run",
        )

        self.MinCapacity = Parameter(
            "MinScaleCapacity",
            Default="0",
            Type="String",
            Description="Number of Min servers to run",
        )
