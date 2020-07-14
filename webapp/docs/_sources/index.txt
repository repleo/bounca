
Welcome to BounCA's documentation!
==================================

`BounCA`_ is a tool to manage your personal SSL certificates and authorities in a central and easy to use interfaces. 
It provides an easy accessible web interface to manage your openssl based *root authority* without the hassle of knowing all the arguments of the command line tools. 
BounCA is also an administration tool for all your signed certificates and revocation lists. 
Create and manage your own X.509 / PKI key and certificate trust infrastructure in a couple of minutes.


The code is open source, and `available on github`_.

.. _BounCA: http://bounca.org/
.. _available on github: http://github.com/repleo/bounca

The main documentation BounCA is organized into a couple sections:

* :ref:`user-docs`
* :ref:`ssl-docs`
* :ref:`about-docs`



.. _user-docs:

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   getting_started
   features
   support

.. _ssl-docs:

.. toctree::
   :maxdepth: 2
   :glob:
   :caption: Certificate Authority
   
   ssl/intro
   ssl/root_pair
   ssl/intermediate_pair
   ssl/sign_server_client_certificates
   ssl/certificate_revocation_list
   ssl/online_certificate_status_protocol
   ssl/appendix


.. _about-docs:

.. toctree::
   :maxdepth: 2
   :caption: About BounCA

   contribution
