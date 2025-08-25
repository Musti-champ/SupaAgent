"""
Script to set up training data structure for the AI model
Run this to prepare your dataset for training
"""

import json
import os
from pathlib import Path
from typing import Dict, List

def create_sample_training_data():
    """Create sample training data structure"""
    
    sample_data = [
        {
            "frontend_code": """
            import React, { useState } from 'react';
            
            function LoginForm() {
                const [email, setEmail] = useState('');
                const [password, setPassword] = useState('');
                
                const handleSubmit = async (e) => {
                    e.preventDefault();
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password })
                    });
                };
                
                return (
                    <form onSubmit={handleSubmit}>
                        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
                        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
                        <button type="submit">Login</button>
                    </form>
                );
            }
            """,
            "backend_code": """
            from fastapi import FastAPI, HTTPException, Depends
            from fastapi.security import HTTPBearer
            from pydantic import BaseModel
            from passlib.context import CryptContext
            import jwt
            
            app = FastAPI()
            security = HTTPBearer()
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            class LoginRequest(BaseModel):
                email: str
                password: str
            
            @app.post("/api/auth/login")
            async def login(request: LoginRequest):
                # Verify user credentials
                user = authenticate_user(request.email, request.password)
                if not user:
                    raise HTTPException(status_code=401, detail="Invalid credentials")
                
                # Generate JWT token
                token = create_access_token(data={"sub": user.email})
                return {"access_token": token, "token_type": "bearer"}
            """,
            "frontend_analysis": "React login form with email/password authentication using fetch API",
            "requirements": ["authentication", "jwt", "password_hashing", "user_management"]
        },
        {
            "frontend_code": """
            import React, { useEffect, useState } from 'react';
            
            interface Product {
                id: number;
                name: string;
                price: number;
                description: string;
            }
            
            function ProductList() {
                const [products, setProducts] = useState<Product[]>([]);
                
                useEffect(() => {
                    fetch('/api/products')
                        .then(res => res.json())
                        .then(data => setProducts(data));
                }, []);
                
                return (
                    <div>
                        {products.map(product => (
                            <div key={product.id}>
                                <h3>{product.name}</h3>
                                <p>${product.price}</p>
                                <p>{product.description}</p>
                            </div>
                        ))}
                    </div>
                );
            }
            """,
            "backend_code": """
            from fastapi import FastAPI, Depends
            from sqlalchemy.orm import Session
            from typing import List
            
            app = FastAPI()
            
            class Product(Base):
                __tablename__ = "products"
                
                id = Column(Integer, primary_key=True, index=True)
                name = Column(String, index=True)
                price = Column(Float)
                description = Column(Text)
            
            class ProductResponse(BaseModel):
                id: int
                name: str
                price: float
                description: str
            
            @app.get("/api/products", response_model=List[ProductResponse])
            async def get_products(db: Session = Depends(get_db)):
                products = db.query(Product).all()
                return products
            """,
            "frontend_analysis": "React product listing component with TypeScript interfaces fetching from REST API",
            "requirements": ["database", "rest_api", "product_management", "sqlalchemy"]
        }
    ]
    
    # Create datasets directory
    datasets_dir = Path("./datasets")
    datasets_dir.mkdir(exist_ok=True)
    
    # Save sample data
    with open(datasets_dir / "sample_training_data.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"Sample training data created at {datasets_dir / 'sample_training_data.json'}")
    print("You can now add your own training examples to this file!")

def create_dataset_template():
    """Create a template for users to add their own training data"""
    
    template = {
        "frontend_code": "// Your frontend code here (React, Vue, Angular, etc.)",
        "backend_code": "// Corresponding backend code here (FastAPI, Django, Express, etc.)",
        "frontend_analysis": "Brief description of what the frontend code does",
        "requirements": ["list", "of", "backend", "requirements"]
    }
    
    with open("./datasets/training_data_template.json", "w") as f:
        json.dump([template], f, indent=2)
    
    print("Training data template created at ./datasets/training_data_template.json")

if __name__ == "__main__":
    create_sample_training_data()
    create_dataset_template()
    
    print("\n" + "="*50)
    print("TRAINING DATA SETUP COMPLETE!")
    print("="*50)
    print("\nNext steps:")
    print("1. Add your own training examples to ./datasets/sample_training_data.json")
    print("2. Use the template in ./datasets/training_data_template.json as a guide")
    print("3. Run the training script when you have enough data")
    print("\nRecommended: Have at least 100+ examples for good results")
