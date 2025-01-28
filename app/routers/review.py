from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.db_depends import get_db
from sqlalchemy import select, insert, update

from app.models.review import Review
from app.models.products import Product

from app.routers.auth import get_current_user
from app.schemas import CreateReview

router = APIRouter(prefix='/review', tags=['reviews'])


async def rating_recalculation(db: Annotated[AsyncSession, Depends(get_db)],
                               product_id: int = None):
    if product_id is not None:
        all_ratings = await db.scalars(select(Review.grade).where(
            Review.product_id == product_id, Review.is_active == True))
        list_of_grades = list(all_ratings)
        average_rating = round(sum(list_of_grades) / len(list_of_grades), 1)
        await db.execute(update(Product).where(Product.id == product_id).values(rating=average_rating))
        await db.commit()


@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    if reviews is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no reviews'
        )
    return reviews.all()

@router.get('/{product_id}')
async def product_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_id: int):
    reviews = await db.scalars(select(Review).where(Review.product_id == product_id, Review.is_active == True))
    if reviews is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Reviews not found'
        )
    return reviews.all()


@router.post('/')
async def add_review(db: Annotated[AsyncSession, Depends(get_db)],
                     create_review: CreateReview,
                     get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_customer'):
        await db.execute(insert(Review).values(product_id=create_review.product_id,
                                               grade=create_review.grade,
                                               comment=create_review.comment,
                                               user_id=get_user.get('id')
                                               ))
        await db.commit()
        await rating_recalculation(db=db, product_id=create_review.product_id)

        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be customer for this action'
        )

@router.delete('/')
async def delete_reviews(db: Annotated[AsyncSession, Depends(get_db)], review_id: int,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    review_delete = await db.scalar(select(Review).where(Review.id == review_id, Review.is_active == True))
    if review_delete is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no review found'
             )
    if get_user.get('is_admin'):
        await db.execute(update(Review).where(Review.id == review_id).values(is_active=False))
        await rating_recalculation(db=db, product_id=review_delete.product_id)

        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Review delete is successful'
        }

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )