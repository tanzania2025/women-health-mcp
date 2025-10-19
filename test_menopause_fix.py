#!/usr/bin/env python3
"""
Test the menopause prediction fix in the complete demo
"""

def test_menopause_fix():
    """Test that the menopause prediction error is fixed."""
    print("🧪 Testing Menopause Prediction Fix")
    print("=" * 40)
    
    try:
        # Test the clinical calculators import
        from clinical_calculators import ClinicalCalculators, MenopausePredictionResult
        print("✅ Clinical calculators imported")
        
        # Test creating calculator instance
        calc = ClinicalCalculators()
        print("✅ Calculator instance created")
        
        # Test the attributes exist
        sample_result = MenopausePredictionResult(
            predicted_age=51.0,
            confidence_interval=(49.0, 53.0),
            current_stage=None,
            time_to_menopause_years=10.0,
            fertility_window_remaining=True,
            risk_factors=[],
            protective_factors=[],
            recommendations=[],
            evidence_base={}
        )
        
        # Check that the correct attribute exists
        assert hasattr(sample_result, 'time_to_menopause_years'), "Missing time_to_menopause_years attribute"
        assert not hasattr(sample_result, 'years_remaining'), "Should not have years_remaining attribute"
        print("✅ Correct attributes verified")
        
        # Test actual prediction call
        result = calc.predict_menopause_timing(
            age=38,
            amh=0.8,
            smoking=False,
            ethnicity="caucasian"
        )
        
        print("✅ Menopause prediction call successful")
        print(f"  - Predicted age: {result.predicted_age:.1f}")
        print(f"  - Time to menopause: {result.time_to_menopause_years:.1f} years")
        print(f"  - Current stage: {result.current_stage.value}")
        
        # Test that the demo code would work
        predicted_age = result.predicted_age
        time_remaining = result.time_to_menopause_years
        current_stage = result.current_stage.value.replace('_', ' ').title()
        
        print("✅ Demo formatting successful")
        print(f"  - Formatted age: {predicted_age:.1f} years")
        print(f"  - Formatted time: {time_remaining:.1f}")
        print(f"  - Formatted stage: {current_stage}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 40)
    print("🎯 Menopause Prediction Fix Status:")
    print("✅ Attribute error resolved")
    print("✅ Method signature corrected")
    print("✅ Clinical calculators working")
    print("✅ Demo integration functional")
    
    print("\n🚀 Clinical calculator section now working:")
    print("Navigate to: Section 2 - Clinical Calculators (ASRM/ESHRE)")
    
    return True

if __name__ == "__main__":
    success = test_menopause_fix()
    if success:
        print("\n🏆 Menopause prediction fix successful!")
    else:
        print("\n❌ Fix verification failed.")