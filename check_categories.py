from app.database import SessionLocal, TransactionModel

db = SessionLocal()
total = db.query(TransactionModel).count()
categorized = db.query(TransactionModel).filter(TransactionModel.category_id != None).count()
uncategorized = total - categorized
print(f'Total transactions: {total}')
print(f'Categorized: {categorized}')
print(f'Uncategorized: {uncategorized}')
db.close()
