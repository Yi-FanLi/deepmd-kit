#ifndef LAMMPS_VERSION_NUMBER
#error Please define LAMMPS_VERSION_NUMBER to yyyymmdd
#endif

#ifdef PAIR_CLASS

PairStyle(deepmd, PairDeepMD)

#else

#ifndef LMP_PAIR_NNP_H
#define LMP_PAIR_NNP_H

#include "pair.h"
#ifdef LMPPLUGIN
#include "DeepPot.h"
#else
#include "deepmd/DeepPot.h"
#endif
#include <fstream>
#include <iostream>

#ifdef HIGH_PREC
#define FLOAT_PREC double
#else
#define FLOAT_PREC float
#endif

namespace LAMMPS_NS {

class PairDeepMD : public Pair {
 public:
  PairDeepMD(class LAMMPS *);
  ~PairDeepMD() override;
  void compute(int, int) override;
  void *extract(const char *, int &) override;
  void settings(int, char **) override;
  void coeff(int, char **) override;
  void init_style() override;
  void write_restart(FILE *) override;
  void read_restart(FILE *) override;
  double init_one(int i, int j) override;
  int pack_reverse_comm(int, int, double *) override;
  void unpack_reverse_comm(int, int *, double *) override;
  void print_summary(const std::string pre) const;
  int get_node_rank();
  std::string get_file_content(const std::string &model);
  std::vector<std::string> get_file_content(
      const std::vector<std::string> &models);

 protected:
  virtual void allocate();
  double **scale;

 private:
  deepmd::DeepPot deep_pot;
  deepmd::DeepPotModelDevi deep_pot_model_devi;
  unsigned numb_models;
  double cutoff;
  int numb_types;
  std::vector<std::vector<double> > all_force;
  std::ofstream fp;
  int out_freq;
  std::string out_file;
  int dim_fparam;
  int dim_aparam;
  int out_each;
  int out_rel;
  int out_rel_v;
  bool single_model;
  bool multi_models_mod_devi;
  bool multi_models_no_mod_devi;
  bool is_restart;
#ifdef HIGH_PREC
  std::vector<double> fparam;
  std::vector<double> aparam;
  double eps;
  double eps_v;
#else
  std::vector<float> fparam;
  std::vector<float> aparam;
  float eps;
  float eps_v;
#endif

  void make_fparam_from_compute(
#ifdef HIGH_PREC
      std::vector<double> &fparam
#else
      std::vector<float> &fparam
#endif
  );
  bool do_compute;
  std::string compute_id;

  void make_ttm_fparam(
#ifdef HIGH_PREC
      std::vector<double> &fparam
#else
      std::vector<float> &fparam
#endif
  );

  void make_ttm_aparam(
#ifdef HIGH_PREC
      std::vector<double> &dparam
#else
      std::vector<float> &dparam
#endif
  );
  bool do_ttm;
  std::string ttm_fix_id;
  int *counts, *displacements;
  tagint *tagsend, *tagrecv;
  double *stdfsend, *stdfrecv;
  std::vector<int> type_idx_map;
};

}  // namespace LAMMPS_NS

#endif
#endif