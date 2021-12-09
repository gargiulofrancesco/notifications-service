# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from notifications.models.notification import Notification  # noqa: E501
from notifications.test import BaseTestCase
from notifications.test.utils import create_notification, get_notifications_by_message_id, get_notification_by_id
from notifications.tasks import deliver_notification
import sys



class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""


    def test_create_notification(self):
        """Test case for create_notification

        create a notification
        """
        notification = Notification()
        notification.user_email = "example@email.com"
        notification.title = "notification title"
        notification.description = "notification description"
        notification.timestamp = "2021-11-30 10:10:00"

        response = self.client.open(
            '/notification',
            method='POST',
            data=json.dumps(notification),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        deliver_notification(1)
        query = get_notification_by_id(1).first()
        assert query.status == 2

        




    def test_delete_notification(self):
        """Test case for delete_notification

        delete a notification for a retreated message
        """

        # message_id of the notification
        msg_id = 3

        # notification not found
        response = self.client.open(
            '/notification/{message}'.format(message=msg_id),
            method='DELETE',
            content_type='application/json')
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # create a notification with is_deleted = False
        create_notification("example@email.com", "title", "description","2021-11-30 10:10:00",msg_id,False,False,2)

        # set notification.is_deleted to True
        response = self.client.open(
            '/notification/{message}'.format(message=msg_id),
            method='DELETE',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        query = get_notifications_by_message_id(msg_id)
        for n in query:
            assert n.is_deleted == True



    def test_get_notifications(self):
        """Test case for get_notifications

        retrieve all (unread) user notifications
        """

        email = "email@email.com"
        title_retrieved = "is-retrieved"
        title_non_retrieved = "not-retrieved"

        # create a non-read, non-deleted, non-delivered notification
        create_notification(email, title_non_retrieved, "description","2021-11-30 10:10:00",1,False,False,1)
        # create a non-read, deleted, delivered notification
        create_notification(email, title_non_retrieved, "description","2021-11-30 10:10:00",1,False,True,2)
        # create a read, non-deleted, delivered notification
        create_notification(email, title_non_retrieved, "description","2021-11-30 10:10:00",1,True,False,2)
        # create a non-read, non-deleted, delivered notification
        create_notification(email, title_retrieved, "description","2021-11-30 10:10:00",1,False,False,2)

        # get all the non-read, non-deleted, delivered notifications
        response = self.client.open(
            '/notifications/{user}'.format(user=email),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        
        # the response contains only the correct notification 
        self.assertIn(bytes(title_retrieved, "utf-8"), response.data)


    def test_notifications_count(self):
        """Test case for notifications_count

        return the number of unread user notifications
        """

        title_retrieved = "is-retrieved"
        title_non_retrieved = "not-retrieved"
        email = "email@email.com"

        # create a non-read, non-deleted, non-delivered notification
        create_notification(email, title_non_retrieved, "description","2021-11-30 10:10:00",1,False,False,1)
        # create a non-read, deleted, delivered notification
        create_notification(email, title_non_retrieved, "description","2021-11-30 10:10:00",1,False,True,2)
        # create a read, non-deleted, delivered notification
        create_notification(email, title_non_retrieved, "description","2021-11-30 10:10:00",1,True,False,2)
        # create 3 non-read, non-deleted, delivered notification
        create_notification(email, title_retrieved, "description","2021-11-30 10:10:00",1,False,False,2)
        create_notification(email, title_retrieved, "description","2021-11-30 10:10:00",1,False,False,2)
        create_notification(email, title_retrieved, "description","2021-11-30 10:10:00",1,False,False,2)

        # the number of notifications the user has to read is 3
        response = self.client.open(
            '/notifications/count/{user}'.format(user=email),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual(response.data.decode('utf-8'), "3\n")


    def test_set_notifications_as_read(self):
        """Test case for set_notifications_as_read

        set all user notifications as read
        """

        email = "email@email.com"

        # create 2 notifications that the user has to read
        create_notification(email, "title", "description","2021-11-30 10:10:00",1,False,False,2)
        create_notification(email, "title", "description","2021-11-30 10:10:00",1,False,False,2)

        # the user has 2 notifications to read
        response = self.client.open(
            '/notifications/count/{user}'.format(user=email),
            method='GET',
            content_type='application/json')
        self.assertEqual(response.data.decode('utf-8'), "2\n")

        # set the notifications of the user as read
        response = self.client.open(
            '/notifications/{user}'.format(user=email),
            method='PUT',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # the user has now 0 notifications to read
        response = self.client.open(
            '/notifications/count/{user}'.format(user=email),
            method='GET',
            content_type='application/json')
        self.assertEqual(response.data.decode('utf-8'), "0\n")
        
 


if __name__ == '__main__':
    import unittest
    unittest.main()
