
class SubscriptionManager:
    pending_users = {}
    subscribed_users = {}

    def is_subscribed(self, user_id):
        return user_id in self.subscribed_users

    def get_all_subscribed_users(self):
        return self.subscribed_users

    def add_user_to_pending(self, message):
        user_id = message.from_user.id
        name = message.text

        self.pending_users[user_id] = name

        print(self.pending_users)

    def add_to_subscribed_users(self, message):
        user_id = message.from_user.id
        username = message.from_user.username

        self.subscribed_users[user_id] = username

        print(self.subscribed_users)

    def remove_user_from_pending(self, message):
        user_id = message.from_user.id
        name = self.pending_users[user_id]
        self.pending_users.pop(user_id)

        return name

    def remove_from_subscribed(self, user_id):
        self.subscribed_users.pop(user_id)
