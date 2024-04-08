# from fastapi import HTTPException,status
# from sqlmodel import Session,select
# from app.routers.authentication.user_authentication import get_password_hash

# from app.models.user import CreateUser, User
# from app.database.db_connection import engine


# def verify_and_register_user(create_user: CreateUser):
#     print(create_user)
#     with Session(engine) as session:
#         user_exists_username = session.get(User, create_user.username)
#         if user_exists_username:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail={"Error": f"User with {create_user.username} already exists"},
#             )
#         user_exists_email = session.exec(
#             select(User).where(User.email == create_user.email)
#         ).first()
#         if user_exists_email:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail={"Error": f"User with {create_user.email} already exists"},
#             )
#         create_user.password=get_password_hash(create_user.password)
#         user=User(**create_user.dict(),disabled=False)
        
#         session.add(user)
#         session.commit()
#         session.refresh(user)
        
#         return user