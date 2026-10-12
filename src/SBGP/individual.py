from dataclasses import dataclass
from typing import Optional, Callable
import numpy as np

@dataclass
class Individual:
    """Represents an individual equation in the population."""
    used_codons: int
    train_loss: float
    validation_loss: Optional[float]
    equation_str: str  # ps - raw equation string
    equation_with_consts: str  # psc - equation with optimized constants
    equation_fn: Callable  # p - function that takes (X, C)
    optimized_consts: np.ndarray  # newc - optimized constants
    equation_fn_with_consts: Callable  # newp - function with constants built in
    equation_fn_transpose: Callable  # p_transpose - function that accepts sklearn format X
    genome: np.ndarray
    n_vars_used: Optional[int] = None
    n_consts_used: Optional[int] = None
    latex: Optional[str] = None


    @classmethod
    def from_evaluation(cls, used_codons: int, genome: np.ndarray, eval_result: tuple):
        """Create Individual from evaluation result."""
        cost, cost_test, ps, psc, p, newc, newp, p_transpose, n_vars_used, n_consts_used = eval_result
        return cls(
            used_codons=used_codons,
            train_loss=cost,
            validation_loss=cost_test,
            equation_str=ps,
            equation_with_consts=psc,
            equation_fn=p,
            optimized_consts=newc,
            equation_fn_with_consts=newp,
            equation_fn_transpose=p_transpose,
            genome=genome.copy(),
            n_vars_used=n_vars_used,
            n_consts_used=n_consts_used
        )
