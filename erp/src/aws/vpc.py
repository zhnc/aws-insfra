from troposphere import GetAZs, Join, Ref, Select, Tags, GetAtt
from troposphere import ec2

from magicdict import MagicDict


class VPC(MagicDict):
    def __init__(self):
        super(VPC, self).__init__()

        self.vpc = ec2.VPC(
            "VPC",
            CidrBlock="172.1.0.0/16",
            InstanceTenancy="default",
            EnableDnsSupport=True,
            EnableDnsHostnames=True,
            Tags=Tags(
                Name=Ref("AWS::StackName")
            ),
        )

        self.internet_gateway = ec2.InternetGateway(
            "InternetGateway",
            Tags=Tags(
                Name=Join("", [Ref("AWS::StackName"), "-internet-gateway"]),
            ),
        )

        self.internet_gateway_attachment = ec2.VPCGatewayAttachment(
            "InternetGatewayAttachment",
            InternetGatewayId=Ref(self.internet_gateway),
            VpcId=Ref(self.vpc),
        )

        self.public_route_table = ec2.RouteTable(
            "PublicRouteTable",
            VpcId=Ref(self.vpc),
            Tags=Tags(
                Name=Join("-", [Ref("AWS::StackName"), "public-route-table"]),
            ),
        )

        self.private_route_table = ec2.RouteTable(
            "PrivateRouteTable",
            VpcId=Ref(self.vpc),
            Tags=Tags(
                Name=Join("-", [Ref("AWS::StackName"), "private-route-table"]),
            ),
        )

        self.vpc_s3_endpoint = ec2.VPCEndpoint(
            "VPCS3Endpoint",
            ServiceName=Join(
                "", ["com.amazonaws.", Ref("AWS::Region"), ".s3"]),
            VpcId=Ref(self.vpc),
            RouteTableIds=[Ref(self.public_route_table),
                           Ref(self.private_route_table)],
        )

        self.route_to_internet = ec2.Route(
            "RouteToInternet",
            DestinationCidrBlock="0.0.0.0/0",
            GatewayId=Ref(self.internet_gateway),
            RouteTableId=Ref(self.public_route_table),
            DependsOn=self.internet_gateway_attachment.title,
        )

        # private subnets

        self.private_subnet_1 = ec2.Subnet(
            "PrivateSubnet1",
            AvailabilityZone=Select(0, GetAZs()),
            CidrBlock="172.1.1.0/24",
            MapPublicIpOnLaunch=False,
            Tags=Tags(
                Name=Join("", [Ref("AWS::StackName"), "-private-subnet-1"]),
            ),
            VpcId=Ref(self.vpc),
        )

        self.private_subnet_1_route_table_association = ec2.SubnetRouteTableAssociation(
            "PrivateSubnet1RouteTableAssociation",
            RouteTableId=Ref(self.private_route_table),
            SubnetId=Ref(self.private_subnet_1),
        )

        self.private_subnet_2 = ec2.Subnet(
            "PrivateSubnet2",
            AvailabilityZone=Select(1, GetAZs()),
            CidrBlock="172.1.2.0/24",
            MapPublicIpOnLaunch=False,
            Tags=Tags(
                Name=Join("", [Ref("AWS::StackName"), "-private-subnet-2"]),
            ),
            VpcId=Ref(self.vpc),
        )

        self.private_subnet_2_route_table_association = ec2.SubnetRouteTableAssociation(
            "PrivateSubnet2RouteTableAssociation",
            RouteTableId=Ref(self.private_route_table),
            SubnetId=Ref(self.private_subnet_2),
        )

        self.private_network_aCL = ec2.NetworkAcl(
            "PrivateNetworkACL",
            VpcId=Ref(self.vpc),
            Tags=Tags(
                Name=Join("", [Ref("AWS::StackName"), "-private-nacl"]),
            ),
        )

        self.private_subnet_1_network_acl_association = ec2.SubnetNetworkAclAssociation(
            "PrivateSubnet1NetworkAclAssociation",
            SubnetId=Ref(self.private_subnet_1),
            NetworkAclId=Ref(self.private_network_aCL),
        )

        self.private_subnet_2_network_acl_association = ec2.SubnetNetworkAclAssociation(
            "PrivateSubnet2NetworkAclAssociation",
            SubnetId=Ref(self.private_subnet_2),
            NetworkAclId=Ref(self.private_network_aCL),
        )

        self.private_network_acl_entry_in = ec2.NetworkAclEntry(
            "PrivateNetworkAclEntryIn",
            CidrBlock="0.0.0.0/0",
            Egress=False,
            NetworkAclId=Ref(self.private_network_aCL),
            Protocol=-1,
            RuleAction="allow",
            RuleNumber=100,
        )

        self.private_network_acl_entry_out = ec2.NetworkAclEntry(
            "PrivateNetworkAclEntryOut",
            CidrBlock="0.0.0.0/0",
            Egress=True,
            NetworkAclId=Ref(self.private_network_aCL),
            Protocol=-1,
            RuleAction="allow",
            RuleNumber=100,
        )

        # public subnets
        self.public_subnet_1 = ec2.Subnet(
            "PublicSubnet1",
            AvailabilityZone=Select(0, GetAZs()),
            CidrBlock="172.1.128.0/24",
            MapPublicIpOnLaunch=True,
            Tags=Tags(
                Name=Join("", [Ref("AWS::StackName"), "-public-subnet-1"]),
            ),
            VpcId=Ref(self.vpc),
        )

        self.public_subnet_1_route_table_association = ec2.SubnetRouteTableAssociation(
            "PublicSubnet1RouteTableAssociation",
            RouteTableId=Ref(self.public_route_table),
            SubnetId=Ref(self.public_subnet_1),

        )

        self.public_subnet_2 = ec2.Subnet(
            "PublicSubnet2",
            AvailabilityZone=Select(1, GetAZs()),
            CidrBlock="172.1.129.0/24",
            MapPublicIpOnLaunch=True,
            Tags=Tags(
                Name=Join("", [Ref("AWS::StackName"), "-public-subnet-2"]),
            ),
            VpcId=Ref(self.vpc),
        )

        self.public_subnet_2_route_table_association = ec2.SubnetRouteTableAssociation(
            "PublicSubnet2RouteTableAssociation",
            RouteTableId=Ref(self.public_route_table),
            SubnetId=Ref(self.public_subnet_2),
        )

        self.nat_eip_1 = ec2.EIP(
            'NatEip',
            Domain="vpc",
        )

        self.nat_1 = ec2.NatGateway(
            'Nat',
            # AllocationId=Ref(self.nat_eip_1),
            AllocationId=GetAtt(self.nat_eip_1, 'AllocationId'),
            SubnetId=Ref(self.public_subnet_1),
            DependsOn=self.nat_eip_1,
        )

        self.nat_route_1=ec2.Route(
            'NatRoute',
            RouteTableId=Ref(self.private_route_table),
            DestinationCidrBlock='0.0.0.0/0',
            NatGatewayId=Ref(self.nat_1),
        )


        #private web subnet
        self.private_web_route_table = ec2.RouteTable(
            "PrivateWebRouteTable",
            VpcId=Ref(self.vpc),
            Tags=Tags(
                Name=Join("-", [Ref("AWS::StackName"), "private-web-route-table"]),
            ),
        )
        self.private_subnet_3 = ec2.Subnet(
            "PrivateSubnet3",
            AvailabilityZone=Select(0, GetAZs()),
            CidrBlock="172.1.3.0/24",
            MapPublicIpOnLaunch=False,
            Tags=Tags(
                Name=Join("", [Ref("AWS::StackName"), "-private-subnet-3"]),
            ),
            VpcId=Ref(self.vpc),
        )

        self.private_subnet_3_route_table_association = ec2.SubnetRouteTableAssociation(
            "PrivateSubnet3RouteTableAssociation",
            RouteTableId=Ref(self.private_web_route_table),
            SubnetId=Ref(self.private_subnet_3),
        )

        self.private_subnet_4 = ec2.Subnet(
            "PrivateSubnet4",
            AvailabilityZone=Select(1, GetAZs()),
            CidrBlock="172.1.4.0/24",
            MapPublicIpOnLaunch=False,
            Tags=Tags(
                Name=Join("", [Ref("AWS::StackName"), "-private-subnet-4"]),
            ),
            VpcId=Ref(self.vpc),
        )

        self.private_subnet_4_route_table_association = ec2.SubnetRouteTableAssociation(
            "PrivateSubnet4RouteTableAssociation",
            RouteTableId=Ref(self.private_web_route_table),
            SubnetId=Ref(self.private_subnet_4),
        )

        self.private_network_aCL_3 = ec2.NetworkAcl(
            "PrivateNetworkACL3",
            VpcId=Ref(self.vpc),
            Tags=Tags(
                Name=Join("", [Ref("AWS::StackName"), "-private-nacl-3"]),
            ),
        )

        self.private_subnet_3_network_acl_association = ec2.SubnetNetworkAclAssociation(
            "PrivateSubnet3NetworkAclAssociation",
            SubnetId=Ref(self.private_subnet_3),
            NetworkAclId=Ref(self.private_network_aCL_3),
        )

        self.private_subnet_4_network_acl_association = ec2.SubnetNetworkAclAssociation(
            "PrivateSubnet4NetworkAclAssociation",
            SubnetId=Ref(self.private_subnet_4),
            NetworkAclId=Ref(self.private_network_aCL_3),
        )

        self.private_network_acl_entry_in_3 = ec2.NetworkAclEntry(
            "PrivateNetworkAclEntryIn3",
            CidrBlock="0.0.0.0/0",
            Egress=False,
            NetworkAclId=Ref(self.private_network_aCL_3),
            Protocol=-1,
            RuleAction="allow",
            RuleNumber=100,
        )

        self.private_network_acl_entry_out_3 = ec2.NetworkAclEntry(
            "PrivateNetworkAclEntryOut3",
            CidrBlock="0.0.0.0/0",
            Egress=True,
            NetworkAclId=Ref(self.private_network_aCL_3),
            Protocol=-1,
            RuleAction="allow",
            RuleNumber=100,
        )

        self.nat_route_3=ec2.Route(
            'NatRoute3',
            RouteTableId=Ref(self.private_web_route_table),
            DestinationCidrBlock='0.0.0.0/0',
            NatGatewayId=Ref(self.nat_1),
        )

        # self.nat_route_3_1=ec2.Route(
        #     'NatRoute31',
        #     RouteTableId=Ref(self.private_web_route_table),
        #     DestinationCidrBlock='172.1.1.0/24',
        #     NatGatewayId=Ref(self.nat_1),
        # )

        # self.nat_route_3_2=ec2.Route(
        #     'NatRoute32',
        #     RouteTableId=Ref(self.private_web_route_table),
        #     DestinationCidrBlock='172.1.2.0/24',
        #     NatGatewayId=Ref(self.nat_1),
        # )

