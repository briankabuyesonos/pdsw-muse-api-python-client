To add new muse_rest helper classes, first create your class files here.
Please take a look at the existing files and feel free to use them as a template.
In order to actually plumb it through to muse_rest, you need to edit the "extendMuseRestClient" function in
"test/python/core/src/sonos/client/internal.py". Don't forget to import your new class file in there as well.