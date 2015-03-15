This tutorial shows how KOALA can help you working with cloud services that are compatible to Amazons Elastic Computing Cloud ([EC2](http://aws.amazon.com/ec2/)). EC2 allows running scalable virtual server instances inside the Amazon server farms using a modified version of the Xen-Hypervisor. Several OpenSource IaaS projects provide the same functionality and implement the EC2 API too.

# First steps with the KOALA Cloud Manager and EC2 #

Using KOALA ist quite easy. All you need is

  * a browser
  * a Google account
  * access to one or more cloud infrastructures
  * some basic knowledge about cloud computing

The browser should be no problem. The Google account is used for the user management and authentication. Without access to one or more cloud infrastructures KOALA itself is worthless and the basic knowledge about cloud computing can be found inside this document.



## Get credentials to a cloud infrastructure ##

You need access to a cloud infrastructure (IaaS) that uses the API of EC2. This is essential because KOALA is a service that helps you working with cloud resources you have access to. KOALA is not a cloud marketplace, so you cannot share cloud resources to others.

The following table shows the cloud infrastructures available that are compatible to the EC2 API.

| **Infrastructure (IaaS)**                 | **Private/Public Cloud** | **License**   | **Supported by KOALA** |
|:------------------------------------------|:-------------------------|:--------------|:-----------------------|
| [Amazon EC2](http://aws.amazon.com/ec2/) | Public Cloud           | proprietary | yes |
| [Eucalyptus](http://open.eucalyptus.com) | Private Cloud          | GPL v3      | yes |
| [Nimbus](http://www.nimbusproject.org)   | Private Cloud          | Apache License v2.0  | yes |
| [OpenNebula](http://www.opennebula.org)  | Private Cloud          | Apache License v2.0  | yes |
| [OpenStack](http://openstack.org) _Nova_ | Private Cloud          | Apache License v2.0  | no |
| [Cloud.com](http://cloud.com)            | Private Cloud          | GPL v3      | no  |
| [Nimbula](http://nimbula.com)            | Public Cloud           | proprietary | no  |

If you don't have any Private Cloud IaaS running, the most easy way is to get access to [Amazon EC2](http://aws.amazon.com/ec2/). If you don't want this because e.g. you don't have a credit card you need a Private Cloud IaaS.

This tutorial focuses on [Amazon EC2](http://aws.amazon.com/ec2/) because it is the most common use case for KOALA.

## Get your credentials into KOALA ##

At first you need to log in with your Google account.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial0_login_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial0_login_small.png)

Inside the **Regions** window you can import your credentials. It is easy to create new region data for all supported IaaS solutions. If you log in the first time into KOALA, you don't have any credentials.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial1_regions_empty_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial1_regions_empty_small.png)

Import your AWS account credentials (Access Key and Secret Access Key). Both will be stored inside the Google Datastore. The Secret Access Key will be stored encrypted.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial2_regions_create_AWS_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial2_regions_create_AWS_small.png)

If your credentials were correct, you have can see the Amazon entry in the table at the **Regions** window. Now, you can start working with this IaaS.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial3_regions_AWS_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial3_regions_AWS_small.png)

After you have import your credentials for at least a single IaaS, you can see that the pull-down list in the center of the header is not empty any longer. With this pull-down menu, you can choose what IaaS shall be used by KOALA. If you have cretentials for more than just a single IaaS region you can use this pull-down menu to switch over to another region.

EC2 itself has four regions and with your AWS credentials you can use them all automatically.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial4_regions_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial4_regions_small.png)

## Availability Zones ##

The **Zones** window gives you a table with the names and the status of the availability zones inside the region you are. For this example you can see we are using the EC2 US East region and inside this region are four availability zones (_us-east-1a_, _us-east-1b_, _us-east-1c_ and _us-east-1d_).

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial8_availabilty_zones_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial8_availabilty_zones_small.png)

## Keypairs ##

To log into your instances, you need a keypair. The keypair consists of a pubic and a private key. The public key is stored inside your instances by the IaaS automatically. The private key need to be stored by yourself at your computer of a portable memory device. With the private key you can log into your instances without a passwort. Using passwords to log into instances is quite unsusual in the cloud. Using keypairs to login is the common way.

If you don't already have a keypair inside the region you want to run instances, you need to create at least one.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial7_keypair1_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial7_keypair1_small.png)

In this example a new keypair _new\_key\_useast_ is created.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial7_keypair2_new_key_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial7_keypair2_new_key_small.png)

When the new keypair is created, a small window appears. Inside this window you can see the private key. You need to save this private key by yourself. Copy it into a new file and adjust the permissions for this file with _chmod 600 filename_.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial7_keypair3_secret_key_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial7_keypair3_secret_key_small.png)

## Security Groups ##

Instances need to be assigned to a security group. You can create new security groups and erase existing groups inside the **Groups** window.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial11_security_group_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial11_security_group_small.png)

Inside every security group you can define what ports for which protocols shall be open. This is the configuration of your instances firewall. If you want to log into your instances via SSH, you need to open port 22 (TCP). If you want to create a web server in the cloud, you need to open at least port 80 (TCP).

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial12_security_group_rules_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial12_security_group_rules_small.png)

## Images ##

When using cloud infrastructures that use [Eucalyptus](http://open.eucalyptus.com), [Nimbus](http://www.nimbusproject.org) or [OpenNebula](http://www.opennebula.org), you can use the **Images** windows to check the images available inside the active region.

When using [Amazon EC2](http://aws.amazon.com/ec2/) we are tortured here by a disadvantage of the EC2 API. Amazon provides no ability to filter the returned list of images on the server side, so you always have to get the whole list or a list of images where you already know the image IDs. The list of all images contains far more than 1000 images. Fetching and processing the whole list of images needs some seconds and this leads to a timeout of the Google App Engine.

When using a Private Cloud with [Eucalyptus](http://open.eucalyptus.com), [Nimbus](http://www.nimbusproject.org) or [OpenNebula](http://www.opennebula.org) it is no problem to fetch a list of all images because inside a Private Cloud will never be as many images as Amazon stores.

As workaround, when using [Amazon EC2](http://aws.amazon.com/ec2/), a list of favorite AMIs can be created by yourself in this window and used to check these images and start instances. This issue is annoying but not dramatic because in most use cases you work with a small choice of images you already know for most of the time.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial5_create_favorites_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial5_create_favorites_small.png)

In this example a few images in the region EC2 US East are stored as favorites.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial6_several_favorites_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial6_several_favorites_small.png)

With the icons in the first columns of the table, instances can be started and fravorites can be erased from this list.

## Start Instances ##

When one or more instances shall be started from an image, lots of information are important.

You have to decide, how many Instances shall be started and if you prefer a specific availability zone. If you don't choose an availability zone, Amazon will decide for you.  At this point you need to set the keypair and the security group too. Also the instance type is important. The instance types are equiped with a different ammount of virtual CPU cores, main memory and storage. The decision of using 64-Bit or 32-Bit architecture is already defined by the image itself. Don't forget the money when using a Public Cloud like [Amazon EC2](http://aws.amazon.com/ec2/). The instancey types differ in the price per hour too.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial9_start_image_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial9_start_image_small.png)

## Instances ##

After you started at least a single instance, you can see inside the **Instances** window all information about your instances.

  * Reservation ID
  * Instance ID
  * Filesystem/Kernel/Ramdisk image
  * Availability Zone
  * Keypair
  * Public DNS
  * Private DNS
  * Launch Time
  * ...

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial13_running_instance_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial13_running_instance_small.png)

Inside this window you can also start another instance with the same key data with just a single click. You can also reboot, stop and terminate your instances. Also the console output can be checked.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial14_console_output_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial14_console_output_small.png)

## Elastic IPs ##

Instances get a public (internal) and a private (external) DNS name automatically, when they are created. If an instance is terminated, the public and private DNS names both are lost.

For implementing sustainable services it is mandatory to use elastic IPs that can be associated to instances and disassociated at any time. The **IPs** window shows a table of the elastic IPs that have already been created by you. It is easy inside this windows to create more elastic IPs and to release them.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial10_elastic_ips_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial10_elastic_ips_small.png)

In this example an elastic IP is associated to the instance we created before. In this window you can decide what instance of you inside this region shall be associated to the elastic IP.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial18_attach_elastic_ip_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial18_attach_elastic_ip_small.png)

After the elastic IP is associated to the instance the **IPs** windows makes it easy to disassociate it as well.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial19_attached_elastic_ip_to_instance_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial19_attached_elastic_ip_to_instance_small.png)

## EBS Volumes ##

Data stored inside instances is not sustainable. After the termination of an instance, its data is lost. Therefore, important data in the cloud need to be stored inside Elastic Block Store (EBS) volumes. Inside the **Volumes** window you can create new volumes and erase existing volumes. A volume can be attached to a single instance and remapped at any time. Using a volume is equal to the work with an unformated block storage device. Volumes can be equiped with any filesystem.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial15_EBS_volumes_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial15_EBS_volumes_small.png)

It is possible to attach volumes to instances and decide which device the volume shall be inside the instance. Volumes can only be attached to instances that run inside the same availability zone and region.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial16_attach_EBS_volumes_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial16_attach_EBS_volumes_small.png)

In the **Volumes** window you can check which volumes are attached to which instances and detach them. In this example, a volume with 5 GB is attached to the instance we created before. Both are inside the availability zone _us-east-1d_ which is inside the region EC2 US East.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial17_attached_EBS_volume_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial17_attached_EBS_volume_small.png)

## Snapshots ##

Inside the **Volumes** window you can also create snapshots of your volumes.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial20_create_snapshot_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial20_create_snapshot_small.png)

The snapshots can be checked and erased inside the **Snapshots** window.

![http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial21_snapshot_created_small.png](http://koalacloud.googlecode.com/svn/trunk/tutorial/images/smaller/tutorial21_snapshot_created_small.png)