# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from notifications.models.notification import Notification  # noqa: E501
from notifications.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_create_notification(self):
        """Test case for create_notification

        create a notification
        """
        notification = Notification()
        response = self.client.open(
            '/notification',
            method='POST',
            data=json.dumps(notification),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_notification(self):
        """Test case for delete_notification

        delete a notification for a retreated message
        """
        response = self.client.open(
            '/notification/{message}'.format(message=56),
            method='DELETE',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_notifications(self):
        """Test case for get_notifications

        retrieve all (unread) user notifications
        """
        response = self.client.open(
            '/notifications/{user}'.format(user='user_example'),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_notifications_count(self):
        """Test case for notifications_count

        return the number of unread user notifications
        """
        response = self.client.open(
            '/notifications/count/{user}'.format(user='user_example'),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_set_notifications_as_read(self):
        """Test case for set_notifications_as_read

        set all user notifications as read
        """
        response = self.client.open(
            '/notifications/{user}'.format(user='user_example'),
            method='PUT',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
