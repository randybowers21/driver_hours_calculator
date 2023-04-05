class InvalidWorkTimesError(Exception):
    def __init__(self, driver_code: str, message: str='Times are invalid'):
        self.driver_code = driver_code
        self.message = f'Error for {driver_code}: {message}'
        super().__init__(self.message)