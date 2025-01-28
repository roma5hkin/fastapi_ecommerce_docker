from pydantic import BaseModel, field_validator


class CreateProduct(BaseModel):
    name: str = 'product'
    description: str = 'description'
    price: int = 100
    image_url: str = 'www.sample.com'
    stock: int = 1
    category_id: int = 0

class CreateCategory(BaseModel):
    name: str = 'category'
    parent_id: int | None

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str

class CreateReview(BaseModel):
    product_id: int
    grade: int
    @field_validator('grade')
    def check_grade(cls, grade: int):
        if grade < 1 or grade > 5:
            raise ValueError('The rating must be between 1 and 5')
        return grade
    comment: str


