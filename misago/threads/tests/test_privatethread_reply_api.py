from django.contrib.auth import get_user_model

from misago.acl.testutils import override_acl

from .. import testutils
from ..models import ThreadParticipant
from .test_privatethreads import PrivateThreadsTestCase


class PrivateThreadReplyApiTestCase(PrivateThreadsTestCase):
    def setUp(self):
        super(PrivateThreadReplyApiTestCase, self).setUp()

        self.thread = testutils.post_thread(self.category, poster=self.user)
        self.api_link = self.thread.get_posts_api_url()

        User = get_user_model()
        self.other_user = User.objects.create_user(
            'BobBoberson', 'bob@boberson.com', 'pass123')

    def test_reply_private_thread(self):
        """api sets other private thread participants sync thread flag"""
        ThreadParticipant.objects.set_owner(self.thread, self.user)
        ThreadParticipant.objects.add_participants(self.thread, [self.other_user])

        response = self.client.post(self.api_link, data={
            'post': "This is test response!"
        })
        self.assertEqual(response.status_code, 200)

        # don't count private thread replies
        self.reload_user()
        self.assertEqual(self.user.threads, 0)
        self.assertEqual(self.user.posts, 0)

        # valid user was flagged to sync
        User = get_user_model()
        self.assertFalse(User.objects.get(pk=self.user.pk).sync_unread_private_threads)
        self.assertTrue(User.objects.get(pk=self.other_user.pk).sync_unread_private_threads)
