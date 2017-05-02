# -*- coding: utf-8 -*-
"""
class Verb

"""
from world.helpers import escape_braces


class VerbHandler:
    """
    class Verb

    A Verb contains methods that allow objects
    to act upon other objects in the world.

    doer, verb, object, preposition, indirect
        TODO: Parse these action forms:
        <verb> (assume subject is also object to make this work after checking for a singular verbable noun)
        <verb> <noun> (This works now)
        <verb> <article> <noun> (check noun for article list after removing possible articles)
        <verb> <preposition> <noun> (check verb for preposition list)
        <verb> <preposition> <article> <noun> (Do both of above)
        <verb> <preposition> <article> <noun> <preposition> <other noun> (look for second preposition options on verb)
        <verb> <preposition> <article> <noun> <preposition> <article> <other noun>

    """
    def __init__(self, subject, verb=None, object=None, preposition=None, indirect=None):
        self.s = subject
        self.v = verb
        self.o = object  # if object else subject
        self.p = preposition
        self.i = indirect
        print('{} tries to {} {}'.format(subject, verb, object))
        if hasattr(self, self.v):
            print("Making attempt to %s" % verb)
            getattr(self, verb)()
        else:
            _default()

    def _default(self):
        self.s.msg('You {} {}.'.format(self.v, self.o))
        self.o.msg('{} tries to {} you.'.format(self.s, self.v))
        self.s.location.msg_contents('{subject} tries to %s {object}.' % self.v,
                                     mapping=dict(subject=self.s, object=self.o),
                                     exclude=[self.s, self.o])
        pass

    def destroy(self):
        """Implements destroying this object."""
        if not self.o.tags.get('pool'):
            pass
        if self.o.location is not None:
            self.o.location = None

    def drop(self):
        """Implements the attempt to drop this object."""
        pose = self.s.ndb.pose
        if self.o.location != self.s:  # If subject is not holding object,
            self.s.msg("You do not have %s." % self.o.get_display_name(self.s))
            return False
        if self.o.db.covered_by:  # You can't drop clothing items that are covered.
            self.s.msg("You can't drop that because it's covered by %s." % self.o.db.covered_by)
            return False
        if self.o.db.worn:
            self.o.remove(self.s, quiet=True)
        if self.o.move_to(self.s.location, quiet=True, use_destination=False):
            self.o.location.msg_contents('%s|g%s|n drops {it}.' % (escape_braces(pose), self.s.key),
                                         from_obj=self.s, mapping=dict(it=self.o))
            self.o.at_drop(self.s)  # Call at_drop() method.
        return True

    def examine(self):
        self.s.player.execute_cmd('examine %s' % self.o.get_display_name(self.s, plain=True))

    def follow(self):
        """Set following agreement - caller follows character"""
        if self.o == self.s:
            self.s.msg('You decide to follow your heart.')
            return
        action = 'follow'
        if self.o.attributes.has('followers') and self.o.db.followers:
            if self.s in self.o.db.followers:
                self.o.db.followers.remove(self.s)
                action = 'stop following'
            else:
                self.o.db.followers.append(caller)
        else:
            self.o.db.followers = [self.s]
        color = 'g' if action == 'follow' else 'r'
        self.s.location.msg_contents('|%s%s|n decides to %s {follower}.'
                                     % (color, self.s.key, action), from_obj=self.s, mapping=dict(follower=self.o))

    def get(self):
        """Implements the attempt to get this object."""
        too_heavy, too_large = False, False
        pose = self.s.ndb.pose
        if self.s == self.o:
            self.s.msg("%sYou|n can't get yourself." % self.s.STYLE)
        elif self.o.location == self.s:
            self.s.msg("%sYou|n already have %s." % (self.s.STYLE, self.o.get_display_name(self.s)))
        elif too_heavy:
            self.s.msg("%sYou|n can't lift %s; it is too heavy." % (self.s.STYLE, self.o.get_display_name(self.s)))
        elif too_large:
            self.s.msg("%sYou|n can lift %s, but it is too large to carry." %
                       (self.s.STYLE, self.o.get_display_name(self.s)))
        elif self.o.move_to(self.s, quiet=True):
            self.s.location.msg_contents('%s|g%s|n takes {it}.' % (escape_braces(pose), self.s.key),
                                         from_obj=self.s, mapping=dict(it=self.o))
            self.o.at_get(self.s)  # calling hook method

    def puppet(self):
        self.s.player.execute_cmd('@ic %s' % self.o.get_display_name(self.s, plain=True))

    def read(self):
        """
        Implements the read command. This simply looks for an
        Attribute "readable_text" on the object and displays that.
        """
        pose = self.o.ndb.power_pose
        read_text = self.o.db.readable_text or self.o.db.desc_brief or self.o.db.desc
        if read_text:  # Attribute read_text is defined.
            self.s.location.msg_contents("%s |g{s}|n reads {o}." % pose,
                                         mapping=dict(s=self.s, o=self.o))
            string = read_text
        else:
            string = "There is nothing to read on %s." % self.o.get_display_name(self.s)
        self.s.msg(string)

    def ride(self):
        """Set riding agreement - caller rides character"""
        if self.o == self.s:
            return
        action = 'ride'
        if self.o.attributes.has('riders') and self.o.db.riders:
            if self.s in self.o.db.riders:
                self.o.db.riders.remove(self.s)
                action = 'stop riding'
            else:
                self.o.db.riders.append(self.s)
        else:
            self.o.db.riders = [self.s]
        # subject is/was riding self invalidate self.s riding anyone else in the room.
        for each in self.s.location.contents:
            if each == self.s or each == self.o or not each.db.riders or self.s not in each.db.riders:
                continue
            each.db.riders.remove(self.s)
        color = 'g' if action == 'ride' else 'r'
        self.s.location.msg_contents('|%s%s|n decides to %s {mount}.'
                                     % (color, self.s.key, action), from_obj=self.s, mapping=dict(mount=self.o))

    def view(self):
        return self.s.player.execute_cmd('look %s' % self.o.get_display_name(self.s, plain=True))