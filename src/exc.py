class NotFoundError(Exception):
    """
    Exception for a NotFound item in db
    """
    def __init__(self, item_id:int):
        super().__init__(f"item_id: {item_id} not found")