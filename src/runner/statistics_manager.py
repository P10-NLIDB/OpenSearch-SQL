import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Union, Tuple

@dataclass
class Statistics:
    corrects: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)
    incorrects: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)
    errors: Dict[str, List[Union[Tuple[str, str], Tuple[str, str, str]]]] = field(default_factory=dict)
    total: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Dict[str, Union[Dict[str, int], List[Tuple[str, str]]]]]:
        """
        Converts the statistics data to a dictionary format.

        Returns:
            Dict[str, Dict[str, Union[Dict[str, int], List[Tuple[str, str]]]]]: The statistics data as a dictionary.
        """
        return {
            "counts": {
                key: {
                    "correct": len(self.corrects.get(key, [])),
                    "incorrect": len(self.incorrects.get(key, [])),
                    "error": len(self.errors.get(key, [])),
                    "total": self.total.get(key, 0)
                }
                for key in self.total
            },
            "ids": {
                key: {
                    "correct": sorted(self.corrects.get(key, [])),
                    "incorrect": sorted(self.incorrects.get(key, [])),
                    "error": sorted(self.errors.get(key, []))
                }
                for key in self.total
            }
        }


class StatisticsManager:
    def __init__(self, result_directory: str):
        """
        Initializes the StatisticsManager.

        Args:
            result_directory (str): The directory to store results.
        """
        self.result_directory = Path(result_directory)
        self.statistics = Statistics()

        # Ensure the statistics file exists
        self.statistics_file_path = self.result_directory / "-statistics.json"
        if not self.statistics_file_path.exists():
            self.statistics_file_path.touch()
            self.dump_statistics_to_file()

    def update_stats(self, db_id: str, question_id: str, evaluation_for: str, result: Dict[str, Any]):
        """
        Updates the statistics based on the evaluation result.

        Args:
            db_id (str): The database ID.
            question_id (str): The question ID.
            evaluation_for (str): The evaluation context.
            result (Dict[str, Any]): The evaluation result.
        """
        exec_res = result["exec_res"]
        exec_err = result["exec_err"]

        self.statistics.total[evaluation_for] = self.statistics.total.get(evaluation_for, 0) + 1

        if exec_res == 1:
            if evaluation_for not in self.statistics.corrects:
                self.statistics.corrects[evaluation_for] = []
            self.statistics.corrects[evaluation_for].append((db_id, question_id))
        else:
            if exec_err == "incorrect answer":
                if evaluation_for not in self.statistics.incorrects:
                    self.statistics.incorrects[evaluation_for] = []
                self.statistics.incorrects[evaluation_for].append((db_id, question_id))
            else:
                if evaluation_for not in self.statistics.errors:
                    self.statistics.errors[evaluation_for] = []
                self.statistics.errors[evaluation_for].append((db_id, question_id, exec_err))

    def dump_statistics_to_file(self):
        """
        Dumps the current statistics to a JSON file.
        """
        with self.statistics_file_path.open('w') as f:
            json.dump(self.statistics.to_dict(), f, indent=4,ensure_ascii=False)
    
    def print_statistics(self):
        """
        Prints the current statistics in a readable format.
        """
        stats_dict = self.statistics.to_dict()

        print("=== Evaluation Statistics ===")
        print()

        counts = stats_dict.get("counts", {})
        ids = stats_dict.get("ids", {})

        for eval_for in sorted(counts.keys()):
            count_data = counts[eval_for]
            id_data = ids.get(eval_for, {})

            print(f"Evaluation Context: {eval_for}")
            print(f"  Total     : {count_data['total']}")
            print(f"  Correct   : {count_data['correct']}")
            print(f"  Incorrect : {count_data['incorrect']}")
            print(f"  Errors    : {count_data['error']}")

            if id_data.get("correct"):
                print(f"    ✓ Correct IDs (sample): {id_data['correct'][:5]}")
            if id_data.get("incorrect"):
                print(f"    ✗ Incorrect IDs (sample): {id_data['incorrect'][:5]}")
            if id_data.get("error"):
                print(f"    ! Error IDs (sample): {id_data['error'][:5]}")
            print()

    def collect_statistics_summary(self) -> Dict[str, Any]:
        """
        Collects evaluation statistics in structured format, including overall execution accuracy.
        
        Returns:
            dict: A summary of evaluation metrics per context and overall accuracy.
        """
        stats_dict = self.statistics.to_dict()
        summary = {}

        counts = stats_dict.get("counts", {})
        ids = stats_dict.get("ids", {})

        total_tasks = 0
        total_correct = 0

        for eval_for in sorted(counts.keys()):
            count_data = counts[eval_for]
            id_data = ids.get(eval_for, {})

            context_total = count_data.get("total", 0)
            context_correct = count_data.get("correct", 0)
            context_incorrect = count_data.get("incorrect", 0)
            context_error = count_data.get("error", 0)

            summary[eval_for] = {
                "total": context_total,
                "correct": context_correct,
                "incorrect": context_incorrect,
                "error": context_error,
                "accuracy": context_correct / context_total if context_total > 0 else 0.0,
                "sample_ids": {
                    "correct": id_data.get("correct", [])[:5],
                    "incorrect": id_data.get("incorrect", [])[:5],
                    "error": id_data.get("error", [])[:5],
                }
            }

            total_tasks += context_total
            total_correct += context_correct

        # Add overall execution accuracy
        summary["overall_accuracy"] = {
            "total": total_tasks,
            "correct": total_correct,
            "accuracy": total_correct / total_tasks if total_tasks > 0 else 0.0
        }

        return summary

