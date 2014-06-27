
        # Integration tests for docmeta
        ztc.ZopeDocFileSuite(
            'docmeta.txt',
            package='plone.docs',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),

