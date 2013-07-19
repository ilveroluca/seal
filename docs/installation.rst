.. _installation:

Installation
========================

Supported Platforms
+++++++++++++++++++

Seal has been tested on `Gentoo <http://www.gentoo.org>`_ and `Ubuntu <http://www.ubuntu.com/>`_. Although
we haven't tested it on other Linux distributions, we expect Seal to work
on them as well. Platforms other than Linux are currently not supported.


Downloading
+++++++++++++++++

You can find the latest release from here:

http://sourceforge.net/projects/biodoop-seal/files/

The documentation refers to this version.

However, the latest release is somewhat old and is missing numerous important
new features.  If you want to try the latest improvements and contributions, you
can checkout the latest stable code from our repository::

  git clone https://github.com/crs4/seal.git

We try to keep the crs4/master branch stable.  Note however that the
documetation for the development version is not up to date.



Detailed Installation Instructions
+++++++++++++++++++++++++++++++++++++


* :ref:`Installing on Ubuntu <installation_ubuntu>` (should work for Debian as well)
* :ref:`Installing on Gentoo <installation_gentoo>`
* :ref:`Generic installation <installation_generic>`

And then, see the deployment instructions/suggestions in the section
:ref:`Installation - Deploying <installation_deploying>`.



Upgrading from previous versions
+++++++++++++++++++++++++++++++++++++

There is no particular upgrade procedure (but see the notes below).  Just
build and deploy Seal following the instructions in the section above.

Upgrading from 0.1.x or 0.2.x
-----------------------------------

Make sure you **copy any custom property settings from the old launcher
scripts** under bin/ into a :ref:`Seal configuration file <seal_config>`.
