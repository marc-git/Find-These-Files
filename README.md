Find-These-Files
================

Python tool for checking if a file or files already exist (with a different name) in a folder before copying.  The tool uses the duplicate files finder (http://sourceforge.net/projects/doubles/) approach by first comparing sizes, then the md5 hash of the first 32kB (or so) and then the full hash if all the rest match up.  It could easily be changed to use another hash if necessary.

This is made for Windows using tkinter.  Porting to linux would be easy but I haven't had time.

The use for the tool came while managing client documents. I would frequently be given a bunch of technical documents and need to integrate them onto my server, not knowing which I already had and which I didn't, and frequently noting that files carried different names even though they were the same.

It has another use for a similar reason.  Often when you use a memory card to copy photos you forget to delete them once copied.  You pick up your camera and take more photos and when you go to copy them on to your PC you realise that you still have other photos there and by that time you have no idea if you copied them or not. To be safe you re-copy the old ones and end up wasting space on your drive.

Warning
--------
I don't make any warranty about the reliability of this script.  I wouldn't use it for critical files without first understanding the underlying methods in the code. You should do the same.
