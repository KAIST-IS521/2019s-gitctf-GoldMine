# GoldMine CA

This is a team project of IS521@KAIST, written by Kangsu Kim, Hwigyeom Kim and Soobin Lee

See the [activity document][https://github.com/KAIST-IS521/2019-Spring/blob/master/Activities/0319.md] to see what this actually do.



This project heavily relies on Docker and Python. Python version should be at least `3.7.x ` to run this program. Only Python `3.7.3` was used in testing the software.

This software is distributed with Dockerfile in order to minimize the effort establishing runtime environment. You can build the image using the following command:

```bash
$ git clone "THIS_REPOSITORY"
$ cd "THIS_REPOSITORY"
$ docker build --tag "YOUR_TAG_NAME" .
```

Note the period `.` at the end of the command. It is required to indicate the build context root for Docker.

When the build is done, you can run the CA using the following command:

```bash
# If you want to see the log:
$ docker run -it --name "YOUR_CONTAINER_NAME" "YOUR_TAG_NAME"

# If you want to run in background:
$ docker run -d --name "YOUR_CONTAINER_NAME" "YOUR_TAG_NAME"
```



### Access Guide

This project uses REST API for an user interaction.

| HTTP Request | Path                    | Input Scheme (Form)                                          | Output                      | Description                                            |
| ------------ | ----------------------- | ------------------------------------------------------------ | --------------------------- | ------------------------------------------------------ |
| GET          | /                       | -                                                            | -                           | Shows Welcome Message                                  |
| POST         | /                       | `uid, password`                                              | User Information            | Shows current user information                         |
| POST         | /image                  | `uid, password`                                              | User Profile Image          | Shows current user image                               |
| POST         | /edit                   | `uid, password`, Optional respectively: `new_password, last_name, first_name, email` | -                           | Edits current user information                         |
| POST         | /edit/image             | `uid, password`, Either of: `default or image=file`          | -                           | Edits current user image                               |
| POST         | /join                   | `uid, password, last_name, first_name, email`                | -                           | Registers new user                                     |
| POST         | /upload-key             | `uid, password, key`                                         | -                           | Uploads user PGP key                                   |
| POST         | /fetch/\<username\>     | `uid, password`                                              | `username`'s certificate    | Fetches `username`'s certificate                       |
| POST         | /revoke/\<fingerprint\> | `uid, password`                                              | -                           | Revokes key and certificate with the given fingerprint |
| POST         | /validate               | `certificate`                                                | Validity of the certificate | Checks the validity of the given certificate           |
| GET          | /crl                    | -                                                            | Certificate Revocation List | Shows the Certificate Revocation List                  |

#### Examples

```bash
# See index page
curl --request GET \
  --url http://YOUR_CA_IP/

# Join CA
curl --request POST \
  --url http://172.17.0.2/join \
  --header 'content-type: application/x-www-form-urlencoded' \
  --data 'uid=tester&password=1234&email=asdf%40ASF.COM&first_name=a&last_name=b'

# View user information
curl --request POST \
  --url http://YOUR_CA_IP/ \
  --header 'content-type: application/x-www-form-urlencoded' \
  --data 'uid=tester&password=1234'

# Edit user information
curl --request POST \
  --url http://YOUR_CA_IP/edit \
  --header 'content-type: application/x-www-form-urlencoded' \
  --data 'uid=tester&password=1234&email=test2%40kaist.ac.kr&first_name=A&last_name=C&new_password=4321'

# View user image
curl --request POST \
  --url http://YOUR_CA_IP/image \
  --header 'content-type: application/x-www-form-urlencoded' \
  --data 'uid=tester&password=1234'

# Edit user image
curl --request POST \
  --url http://YOUR_CA_IP/edit/image \
  --form uid=tester \
  --form password=1234 \
  --form image=YOUR_IMAGE

# Upload user key
curl --request POST \
  --url http://YOUR_CA_IP/upload-key \
  --header 'content-type: application/x-www-form-urlencoded' \
  --data 'uid=tester&password=1234&key=YOUR_KEY'

# Download user certificate
curl --request POST \
  --url http://YOUR_CA_IP/fetch/USERNAME_TO_DOWNLOAD \
  --header 'content-type: application/x-www-form-urlencoded' \
  --data 'uid=tester&password=1234'

# Validate user certificate
curl --request POST \
  --url http://YOUR_CA_IP/validate \
  --header 'content-type: application/x-www-form-urlencoded' \
  --data certificate=YOUR_CERTIFICATE

# Revoke user key
curl --request POST \
  --url http://YOUR_CA_IP/revoke/YOUR_FINGERPRINT \
  --header 'content-type: application/x-www-form-urlencoded' \
  --data 'uid=tester&password=1234'

# Get CRL
curl --request GET \
  --url http://172.17.0.2/crl
```
