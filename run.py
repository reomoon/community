from app import create_app

app = create_app()

if __name__ == '__main__':
    # 데이터베이스 테이블 생성
    with app.app_context():
        from app.models import db
        db.create_all()
        print("데이터베이스 테이블이 생성되었습니다.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)