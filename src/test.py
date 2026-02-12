"""class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        for i_index, i in enumerate(nums):
            for j_index, j in enumerate(nums):
                if i_index == j_index:
                    continue
                elif i + j == target:
                    return [i_index, j_index]"""
                
class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        hashmap = {}
        for i_index, i in enumerate(nums):
            complement = target - i
            if complement in hashmap:
                return [hashmap[complement], i_index]
            hashmap[i] = i_index



# ----------------------------
# Test Cases
# ----------------------------
test_cases = [
    {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [[0, 1]]},
    {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [[1, 2]]},
    {"input": {"nums": [3, 3], "target": 6}, "expected": [[0, 1]]},
    # Multiple correct pairs possible
    {"input": {"nums": [1, 5, 3, 7], "target": 8}, "expected": [[1, 2], [0, 3]]},
    {"input": {"nums": [0, 4, 3, 0], "target": 0}, "expected": [[0, 3]]},
    {"input": {"nums": [-3, 4, 3, 90], "target": 0}, "expected": [[0, 2]]},
    {"input": {"nums": [5, 75, 25], "target": 100}, "expected": [[1, 2]]},
    {"input": {"nums": [1, 2], "target": 3}, "expected": [[0, 1]]},
    {"input": {"nums": [0, -1, 2, -3, 1], "target": -2}, "expected": [[3, 4]]},
    {"input": {"nums": [10, 20, 30, 40, 50], "target": 70}, "expected": [[1, 4], [2, 3]]},
]

# ----------------------------
# Run Tests
# ----------------------------
solver = Solution()

for i, test in enumerate(test_cases, 1):
    nums = test["input"]["nums"]
    target = test["input"]["target"]
    expected_list = test["expected"]

    result = solver.twoSum(nums, target)

    # Check if result matches any valid expected pair (in any order)
    is_correct = any(
        result == exp or result == exp[::-1] for exp in expected_list
    )

    if is_correct:
        print(f"[PASS] Test {i}: result = {result}")
    else:
        print(f"[FAIL] Test {i}: expected one of {expected_list}, got {result}")