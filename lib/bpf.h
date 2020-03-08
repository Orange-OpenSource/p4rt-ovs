/*
 * Copyright 2018 Orange
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#ifndef BPF_H
#define BPF_H 1

#include <stdint.h>

#include "util.h"
#include "bpf/ubpf.h"
#include "bpf/ubpf_int.h"
#include "dp-packet.h"
#include "bpf/lookup3.h"


struct ubpf_vm *create_ubpf_vm(const ovs_be16 prog_id);

bool load_bpf_prog(struct ubpf_vm *vm, size_t code_len, char *code);

void *ubpf_map_lookup(const struct ubpf_map *map, void *key);

int ubpf_map_update(struct ubpf_map *map, const void *key, void *item);

//bpf_result  ubpf_handle_packet(struct ubpf_vm *vm, struct dp_packet *packet);

bpf_result run_bpf_prog(const struct dp_packet *packet, struct ubpf_vm *vm);

static inline bool
ubpf_is_empty(struct ubpf_vm *vm) {
    return vm->insts == NULL;
}

#endif
