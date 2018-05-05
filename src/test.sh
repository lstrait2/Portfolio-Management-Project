# test script to run all tests
# use chmod u+x test.sh if unable to run
echo ""
echo "Running model tests"
echo ""
python test_model.py
echo ""
echo "Running API test"
echo ""
python test_api.py