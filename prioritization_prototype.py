#!/usr/bin/env python3
"""
Prototype prioritization algorithm for complaints
"""

import math
from datetime import datetime, timedelta
from typing import List, Dict, Any

class PrioritizationPrototype:
    """Prototype class for complaint prioritization"""
    
    def __init__(self):
        # Weights for different factors
        self.W_UPVOTES = 2.0      # Weight for upvotes
        self.W_TIME = 0.05        # Weight for time decay (hours)
        self.W_STATUS = 1.5       # Weight for status
        self.W_LOCATION = 1.0     # Weight for location priority
        
        # Status priorities
        self.STATUS_PRIORITIES = {
            'pending': 1.0,
            'in_progress': 0.8,
            'resolved': 0.1
        }
        
        # Location priorities (can be customized)
        self.LOCATION_PRIORITIES = {
            'downtown': 1.2,
            'residential': 1.0,
            'commercial': 1.1,
            'industrial': 0.9
        }
    
    def calculate_priority_score(self, complaint: Dict[str, Any]) -> float:
        """Calculate priority score for a complaint"""
        try:
            # Base score
            score = 0.0
            
            # Upvotes factor
            upvotes = complaint.get('upvote_count', 0)
            upvote_score = math.log(1 + upvotes) * self.W_UPVOTES
            score += upvote_score
            
            # Time decay factor
            created_at = complaint.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                
                hours_old = (datetime.now() - created_at).total_seconds() / 3600
                time_score = math.exp(-hours_old / 24) * self.W_TIME  # Decay over 24 hours
                score += time_score
            
            # Status factor
            status = complaint.get('status', 'pending')
            status_score = self.STATUS_PRIORITIES.get(status, 1.0) * self.W_STATUS
            score += status_score
            
            # Location factor
            location = complaint.get('location', '').lower()
            location_score = 1.0
            for loc_key, priority in self.LOCATION_PRIORITIES.items():
                if loc_key in location:
                    location_score = priority
                    break
            score += location_score * self.W_LOCATION
            
            return round(score, 2)
            
        except Exception as e:
            print(f"Error calculating priority score: {e}")
            return 0.0
    
    def prioritize_complaints(self, complaints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize a list of complaints"""
        try:
            # Calculate priority scores
            for complaint in complaints:
                complaint['priority_score'] = self.calculate_priority_score(complaint)
            
            # Sort by priority score (descending)
            complaints.sort(key=lambda x: x['priority_score'], reverse=True)
            
            return complaints
            
        except Exception as e:
            print(f"Error prioritizing complaints: {e}")
            return complaints
    
    def get_priority_explanation(self, complaint: Dict[str, Any]) -> Dict[str, Any]:
        """Get explanation of priority calculation"""
        try:
            explanation = {
                'complaint_id': complaint.get('id'),
                'title': complaint.get('title'),
                'final_score': 0.0,
                'factors': {}
            }
            
            # Upvotes factor
            upvotes = complaint.get('upvote_count', 0)
            upvote_score = math.log(1 + upvotes) * self.W_UPVOTES
            explanation['factors']['upvotes'] = {
                'count': upvotes,
                'score': round(upvote_score, 2),
                'weight': self.W_UPVOTES
            }
            
            # Time factor
            created_at = complaint.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                
                hours_old = (datetime.now() - created_at).total_seconds() / 3600
                time_score = math.exp(-hours_old / 24) * self.W_TIME
                explanation['factors']['time'] = {
                    'hours_old': round(hours_old, 2),
                    'score': round(time_score, 2),
                    'weight': self.W_TIME
                }
            
            # Status factor
            status = complaint.get('status', 'pending')
            status_score = self.STATUS_PRIORITIES.get(status, 1.0) * self.W_STATUS
            explanation['factors']['status'] = {
                'status': status,
                'score': round(status_score, 2),
                'weight': self.W_STATUS
            }
            
            # Location factor
            location = complaint.get('location', '').lower()
            location_score = 1.0
            for loc_key, priority in self.LOCATION_PRIORITIES.items():
                if loc_key in location:
                    location_score = priority
                    break
            explanation['factors']['location'] = {
                'location': complaint.get('location'),
                'score': round(location_score * self.W_LOCATION, 2),
                'weight': self.W_LOCATION
            }
            
            # Calculate final score
            explanation['final_score'] = round(
                upvote_score + time_score + status_score + (location_score * self.W_LOCATION), 2
            )
            
            return explanation
            
        except Exception as e:
            print(f"Error generating explanation: {e}")
            return {'error': str(e)}

def main():
    """Test the prioritization prototype"""
    print("🧪 Prioritization Prototype Test")
    print("=" * 40)
    
    # Sample complaints
    sample_complaints = [
        {
            'id': 1,
            'title': 'Pothole on Main Street',
            'description': 'Large pothole causing traffic issues',
            'location': 'Main Street, Downtown',
            'status': 'pending',
            'upvote_count': 15,
            'created_at': datetime.now() - timedelta(hours=2)
        },
        {
            'id': 2,
            'title': 'Broken Streetlight',
            'description': 'Streetlight not working at night',
            'location': 'Oak Avenue, Residential',
            'status': 'in_progress',
            'upvote_count': 8,
            'created_at': datetime.now() - timedelta(hours=12)
        },
        {
            'id': 3,
            'title': 'Garbage Collection Issue',
            'description': 'Garbage not collected for 3 days',
            'location': 'Pine Street, Commercial',
            'status': 'resolved',
            'upvote_count': 25,
            'created_at': datetime.now() - timedelta(hours=48)
        }
    ]
    
    # Initialize prioritization
    prioritizer = PrioritizationPrototype()
    
    # Test individual complaint
    print("\n📊 Individual Complaint Analysis:")
    for complaint in sample_complaints:
        explanation = prioritizer.get_priority_explanation(complaint)
        print(f"\nComplaint {complaint['id']}: {complaint['title']}")
        print(f"Final Score: {explanation['final_score']}")
        for factor, details in explanation['factors'].items():
            print(f"  {factor}: {details}")
    
    # Test prioritization
    print("\n🏆 Prioritized Complaints:")
    prioritized = prioritizer.prioritize_complaints(sample_complaints.copy())
    for i, complaint in enumerate(prioritized, 1):
        print(f"{i}. {complaint['title']} (Score: {complaint['priority_score']})")

if __name__ == "__main__":
    main()
