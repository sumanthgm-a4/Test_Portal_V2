from djongo import models
from bson import ObjectId

class TestQuestion(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId, editable=False)
    question_name = models.CharField(max_length=50)
    question_desc = models.TextField(max_length=500)
    visible_test_cases = models.JSONField(default=list)  # Stores a list of dictionaries
    hidden_test_cases = models.JSONField(default=list)   # Stores a list of dictionaries

    def __str__(self):
        return self.question_name
