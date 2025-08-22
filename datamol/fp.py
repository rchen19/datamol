from typing import Union
from typing import Optional
from typing import Any

import numpy as np

import datamol as dm

from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem import rdmolops
from rdkit.Chem import rdReducedGraphs
from rdkit.Chem.EState import Fingerprinter as EStateFingerprinter
from rdkit.Avalon import pyAvalonTools
from rdkit.Chem import rdFingerprintGenerator

from rdkit.DataStructs.cDataStructs import SparseBitVect
from rdkit.DataStructs.cDataStructs import UIntSparseIntVect
from rdkit.DataStructs.cDataStructs import IntSparseIntVect
from rdkit.DataStructs.cDataStructs import LongSparseIntVect
from rdkit.DataStructs.cDataStructs import ExplicitBitVect
from rdkit.DataStructs.cDataStructs import ULongSparseIntVect

_FP_GENERATORS = {
    "ecfp": rdFingerprintGenerator.GetMorganGenerator,
    "fcfp": rdFingerprintGenerator.GetMorganGenerator,
    "topological": rdFingerprintGenerator.GetTopologicalTorsionGenerator,
    "atompair": rdFingerprintGenerator.GetAtomPairGenerator,
    "rdkit": rdFingerprintGenerator.GetRDKitFPGenerator,
    "ecfp-count": rdFingerprintGenerator.GetMorganGenerator,
    "fcfp-count": rdFingerprintGenerator.GetMorganGenerator,
    "topological-count": rdFingerprintGenerator.GetTopologicalTorsionGenerator,
    "atompair-count": rdFingerprintGenerator.GetAtomPairGenerator,
    "rdkit-count": rdFingerprintGenerator.GetRDKitFPGenerator,
}

_FP_FUNCS = {
    "maccs": rdMolDescriptors.GetMACCSKeysFingerprint,
    "pattern": rdmolops.PatternFingerprint,
    "layered": rdmolops.LayeredFingerprint,
    "erg": rdReducedGraphs.GetErGFingerprint,
    # NOTE(hadim): bad for pickling?
    "estate": lambda x, **args: EStateFingerprinter.FingerprintMol(x)[0],
    "avalon-count": pyAvalonTools.GetAvalonCountFP,
    "avalon": pyAvalonTools.GetAvalonFP,
    **_FP_GENERATORS,
}

_FP_DEFAULT_ARGS = {
    "maccs": {},
    "avalon": {
        "nBits": 512,
        "isQuery": False,
        "resetVect": False,
        "bitFlags": pyAvalonTools.avalonSimilarityBits,
    },
    "ecfp": {
        "radius": 3,  # ECFP6 - not the RDKit default (ECFP4)
        "fpSize": 2048,
        "includeChirality": False,
        "useBondTypes": True,
        "countSimulation": False,
        "countBounds": None,
        "atomInvariantsGenerator": None,
        "bondInvariantsGenerator": None,
    },
    "fcfp": {
        "radius": 2,
        "fpSize": 2048,
        "includeChirality": False,
        "useBondTypes": True,
        "countSimulation": False,
        "countBounds": None,
        "atomInvariantsGenerator": rdFingerprintGenerator.GetMorganFeatureAtomInvGen(),
        "bondInvariantsGenerator": None,
    },
    "topological": {
        "includeChirality": False,
        "torsionAtomCount": 4,
        "countSimulation": True,
        "countBounds": None,
        "fpSize": 2048,
        "atomInvariantsGenerator": None,
    },
    "atompair": {
        "minDistance": 1,
        "maxDistance": 30,
        "includeChirality": False,
        "use2D": True,
        "countSimulation": True,
        "countBounds": None,
        "fpSize": 2048,
        "atomInvariantsGenerator": None,
    },
    "rdkit": {
        "minPath": 1,
        "maxPath": 7,
        "useHs": True,
        "branchedPaths": True,
        "useBondOrder": True,
        "countSimulation": False,
        "countBounds": None,
        "fpSize": 2048,
        "numBitsPerFeature": 2,
        "atomInvariantsGenerator": None,
    },
    "pattern": {
        "fpSize": 2048,
        "atomCounts": [],
        "setOnlyBits": None,
        "tautomerFingerprints": False,
    },
    "layered": {
        "fpSize": 2048,
        "minPath": 1,
        "maxPath": 7,
        "atomCounts": [],
        "setOnlyBits": None,
        "branchedPaths": True,
        "fromAtoms": 0,
    },
    "secfp": {
        "n_permutations": 128,
        "nBits": 2048,
        "radius": 3,
        "min_radius": 1,
        "rings": True,
        "kekulize": False,
        "isomeric": False,
        "seed": 0,
    },
    "erg": {"atomTypes": 0, "fuzzIncrement": 0.3, "minPath": 1, "maxPath": 15},
    "estate": {},
    # COUNTING FP
    "avalon-count": {
        "nBits": 512,
        "isQuery": False,
        "bitFlags": pyAvalonTools.avalonSimilarityBits,
    },
    "ecfp-count": {
        "radius": 3,  # ECFP6 - not the RDKit default (ECFP4)
        "fpSize": 2048,
        "includeChirality": False,
        "useBondTypes": True,
        "countSimulation": False,
        "countBounds": None,
        "atomInvariantsGenerator": None,
        "bondInvariantsGenerator": None,
    },
    "fcfp-count": {
        "radius": 2,
        "fpSize": 2048,
        "includeChirality": False,
        "useBondTypes": True,
        "countSimulation": False,
        "countBounds": None,
        "atomInvariantsGenerator": rdFingerprintGenerator.GetMorganFeatureAtomInvGen(),
        "bondInvariantsGenerator": None,
    },
    "topological-count": {
        "includeChirality": False,
        "torsionAtomCount": 4,
        "countSimulation": True,
        "countBounds": None,
        "fpSize": 2048,
        "atomInvariantsGenerator": None,
    },
    "atompair-count": {
        "minDistance": 1,
        "maxDistance": 30,
        "includeChirality": False,
        "use2D": True,
        "countSimulation": True,
        "countBounds": None,
        "fpSize": 2048,
        "atomInvariantsGenerator": None,
    },
    "rdkit-count": {
        "minPath": 1,
        "maxPath": 7,
        "useHs": True,
        "branchedPaths": True,
        "useBondOrder": True,
        "countSimulation": False,
        "countBounds": None,
        "fpSize": 2048,
        "numBitsPerFeature": 1,
        "atomInvariantsGenerator": None,
    },
}


def fp_to_array(
    fp: Union[np.ndarray, SparseBitVect, ExplicitBitVect, UIntSparseIntVect]
) -> np.ndarray:
    """Convert rdkit fingerprint to numpy array.

    Note:
        This implementation has shown to be faster than using `DataStructs.ConvertToNumpyArray`
        by a factor of ~4. See https://github.com/rdkit/rdkit/discussions/3863.

    Args:
        fp: The fingerprint.
    """

    if isinstance(fp, np.ndarray):
        fp_out = fp

    elif isinstance(fp, SparseBitVect):
        tmp = np.zeros(fp.GetNumBits(), dtype=int)
        on_bits = np.array(fp.GetOnBits())
        tmp[on_bits] = 1
        fp_out = tmp

    elif isinstance(fp, ExplicitBitVect):
        fp_out = np.frombuffer(fp.ToBitString().encode(), "u1") - ord("0")

    elif isinstance(
        fp,
        (
            UIntSparseIntVect,
            IntSparseIntVect,
            LongSparseIntVect,
            ULongSparseIntVect,
        ),
    ):
        tmp = np.zeros(fp.GetLength(), dtype=int)
        bit_idx, values = np.array(list(fp.GetNonzeroElements().items())).T
        tmp[bit_idx] = values
        fp_out = tmp

    else:
        raise ValueError(
            f"The fingerprint of type '{type(fp)}' is not supported. "
            "Please open a ticket at https://github.com/datamol-io/datamol/issues."
        )

    return fp_out


def to_fp(
    mol: Union[str, Chem.rdchem.Mol],
    as_array: bool = True,
    fp_type: str = "ecfp",
    fold_size: Optional[int] = None,
    **fp_args: Any,
) -> Optional[Union[np.ndarray, SparseBitVect, ExplicitBitVect]]:
    """Compute the molecular fingerprint given a molecule or a SMILES.

    Args:
        mol: a molecule or a SMILES.
        as_array: Whether to return a numpy array of an RDKit vec. Default to True.
        fp_type: The type of the fingerprint. See `dm.list_supported_fingerprints()` for a
            complete list.
        fold_size: If set, fold the fingerprint to the `fold_size`. If set, returned array is
            always a numpy array.
        **fp_args: Arguments to build the fingerprint. Refer to the official RDKit documentation.

    Returns:
        A fingerprint vector or None
    """

    # Get fp function
    fp_func = _FP_FUNCS.get(fp_type)

    if fp_func is None:
        raise ValueError(
            f"The fingerprint '{fp_type}' is not available. Use `dm.list_supported_fingerprints()` to "
            "get a complete list of the available fingerprints."
        )

    # Convert input to mol if needed
    if isinstance(mol, str):
        mol_obj = dm.to_mol(mol)
    else:
        mol_obj = mol

    if mol_obj is None:
        raise ValueError(f"It seems like the input molecule '{mol}' is invalid.")

    mol = mol_obj

    # Insert default values.
    for key, value in _FP_DEFAULT_ARGS[fp_type].items():
        fp_args.setdefault(key, value)

    # Compute the fingerprint
    if fp_type in _FP_GENERATORS:
        fp_func = fp_func(**fp_args)
        if fp_type.endswith("-count"):
            fp = fp_func.GetCountFingerprint(mol)
        else:
            fp = fp_func.GetFingerprint(mol)
    else:
        fp = fp_func(mol, **fp_args)

    # Fold the fp if needed.
    if fold_size is not None:
        fp = fold_count_fp(fp, dim=fold_size)

    # Convert to a numpy array
    if not fold_size and as_array:
        fp = fp_to_array(fp)

    return fp


def list_supported_fingerprints():
    """Return the supported fingerprints in datamol."""

    return _FP_FUNCS


def fold_count_fp(
    fp: Union[np.ndarray, SparseBitVect, ExplicitBitVect],
    dim: int = 1024,
    binary: bool = False,
) -> np.ndarray:
    """Fast folding of a count fingerprint to the specified dimension.

    Args:
        fp: A fingerprint.
        dim: The dimension of the folded array.
        binary: Whether to fold into a binary array or take use a count vector.

    Returns:
        folded: returns folded array to the provided dimension.
    """
    if isinstance(
        fp,
        (
            UIntSparseIntVect,
            IntSparseIntVect,
            LongSparseIntVect,
            ULongSparseIntVect,
        ),
    ):
        tmp = fp.GetNonzeroElements()

    elif isinstance(fp, SparseBitVect):
        on_bits = fp.GetOnBits()
        tmp = dict(zip(on_bits, np.ones(len(on_bits))))

    else:
        raise ValueError(f"The fingerprint is of wrong type: {type(fp)}")

    # ON bits dict to (i, v)
    i = np.array(list(tmp.keys())) % dim
    v = np.array(list(tmp.values()))

    # Fold indices
    i = i % dim

    # Create the folded fp
    folded = np.zeros(dim, dtype="int")
    np.add.at(folded, i, v)

    if binary:
        folded = np.clip(folded, a_min=0, a_max=1)

    return folded
