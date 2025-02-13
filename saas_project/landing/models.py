from django.db import models

class AxleLoadData(models.Model):
    axle_unit = models.CharField(max_length=5)
    allowable_mass = models.FloatField()
    actual_mass = models.FloatField()
    no_of_axles = models.IntegerField()
    axle_type = models.CharField(max_length=20)
    w_spc_a = models.FloatField()
    w_spc_b = models.FloatField()
    type_pressure = models.FloatField()
    total_mass = models.FloatField()
    wheel_track = models.FloatField()
    av_no = models.CharField(max_length=10)
    laden_length = models.FloatField()
    laden_width = models.FloatField()
    laden_height = models.FloatField()
    total_distance = models.FloatField()
    distance_escorted = models.FloatField()
    no_of_escorts = models.IntegerField()
    rural_speed = models.FloatField()
    engineer_fee = models.BooleanField(default=False)
    weekend_travel = models.BooleanField(default=False)
    mobile_crane = models.BooleanField(default=False)
    province = models.CharField(max_length=2)
    calculated_fee = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Permit for {self.axle_unit} - {self.total_mass} kg"
    

class Constant(models.Model):
    id = models.BigIntegerField(primary_key=True)
    dbfinyear = models.IntegerField()  # Financial Year
    dbconstname = models.CharField(max_length=100)  # Constant Name
    dbprovcode = models.CharField(max_length=10)  # Province Code
    dbconstvalue = models.FloatField()  # Editable Value

    def __str__(self):
        return f"{self.dbConstName} - {self.dbConstValue}"    
