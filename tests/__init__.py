from typing import Type


class test:

    @classmethod
    @property
    def db(cls):
        return 1

    @classmethod
    def say(cls):
        print(cls.db)


test.say()