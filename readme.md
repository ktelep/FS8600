# _FS8600 CLI Wrapper_

_Description: This module provides a wrapper for accessing the SSH CLI on Dell FluidFS FS8600 (and possibly 7600) NAS Hardware_

## Requirements

1. _paramiko and by proxy, pycrypto_

## Usage

1.  _Instantiate your FS8600 device_

```
from FS8600 import FS8600

my_nas = FS8600("127.0.0.1","myuser","mypass")
```

2.  _Execute commands (aka...Profit!)_

All functions turn into CLI commands dynamically, replacing spaces with _ and dash with __ .
Unnamed arguments in the CLI are positional 
Named arguments in the CLI are kwargs

Examples:
```
Functions with no parameters
At the CLI:   system general cluster-name view
In Python:  my_nas.system_general_cluster__name_view()

Function with only unnamed arguments
At the CLI:   access nas-volume delete MyVolume
In Python:  my_nas.access_nas__volumes_delete("MyVolume")

Function with unnamed arguments and named arguments
At the CLI:   access nas-volumes add MyVolume 300 GB -security_style NTFS
In Python:  self.access_nas__volumes_add("MyVolume","300","GB",security_style="NTFS")
```

3. _Other ways to execute commands_

There is also a function for passing a raw command to the NAS:
```
In Python:   ny_nas.raw_nas_command("access nas-volumes add MyVolume 300 GB -security_style NTFS")
```

There are some helper functions also available in the module, I encourage you to look at them.
