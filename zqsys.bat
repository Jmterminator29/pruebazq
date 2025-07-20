echo off
net use lpt1 /Delete
net use lpt1 \\SERVER2\EPSON /Persistent:YES
pause