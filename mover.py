from docker import Client, tls
import json
from os import path, environ


class CpDockerImages(object):
  """
  Copies docker image from one repo to another
  """
  def __init__(self):
    self.src_reg_username = ""
    self.src_reg_password = ""
    self.dst_reg_username = ""
    self.dst_reg_password = ""
    self.src_repository = ""
    self.src_tag = ""
    self.dst_repository = ""
    self.dst_tag = ""
    self.client = self.create_client()
    self.copy_image()

  def cp_image(self):
    """
    Copies docker image from one repo to another
    :return: None
    """
    self.download_image()
    self.tag_downloaded_image()
    self.upload_image()

  def create_client(self):
    """
    Create docker client
    :return: None
    """
    tls_config = None
    if environ["DOCKER_TLS_VERIFY"] == "1":
      cert_path = environ["DOCKER_CERT_PATH"]

      tls_config = tls.TLSConfig(
        client_cert=(path.join(cert_path, 'cert.pem'),
                     path.join(cert_path, 'key.pem')),
        ca_cert=path.join(cert_path, 'ca.pem'),
        verify=True
      )
    return Client(base_url=environ["DOCKER_HOST"], tls=tls_config)

  def authenticate_user(self, username, password):
    """
    Authenticate the client with given username and password
    :param username: username to use for authentication
    :param password: password to use for authentication
    :return: None or raises Exception
    """
    success = self.client.login(username=username, password=password)

    if not success:
      raise Exception()

  @property
  def _src_image(self):
    """
    Get src image name
    :return: user/repo
    """
    return self.src_reg_username + "/" + self.src_repository

  @property
  def _dst_image(self):
    """
    Get dst image name
    :return: user/repo
    """
    return self.dst_reg_username + "/" + self.dst_repository

  def download_image(self):
    """
    Download image after authenticating user with Destination
    registry credentials
    :return:
    """
    self.authenticate_user(self.src_reg_username, self.src_reg_password)

    for line in self.client.pull(self._src_image,
                                 tag=self.src_tag,
                                 stream=True):
      print(json.dumps(json.loads(line), indent=4))

  def tag_downloaded_image(self):
    """
    Tag downloaded image from src registry to dst registry
    :return:
    """
    tagged = self.client.tag(self._src_image,
                             self._dst_image,
                             self.dst_tag)
    if not tagged:
      raise Exception()

  def upload_image(self):
    """
    Upload image after authenticating user with Destination
    registry credentials
    :return: None
    """
    self.authenticate_user(self.dst_reg_username, self.dst_reg_password)

    for line in self.client.push(self._dst_image,
                                 tag=self.dst_tag,
                                 stream=True):
      print(json.dumps(json.loads(line), indent=4))


if __name__ == "__main__":
  copier = CpDockerImages()
  copier.cp_image()
