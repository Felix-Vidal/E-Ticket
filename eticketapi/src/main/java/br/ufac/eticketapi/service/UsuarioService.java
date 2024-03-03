package br.ufac.eticketapi.service;

import java.util.List;

import org.springframework.stereotype.Service;

import br.ufac.eticketapi.model.Usuario;
import br.ufac.eticketapi.repository.UsuarioRepository;

@Service
public class UsuarioService implements IService<Usuario>{

    private final UsuarioRepository repo;

    public UsuarioService(UsuarioRepository repo) {
        this.repo = repo;
    }

    @Override
    public List<Usuario> get() {
        return repo.findAll();
    }

    @Override
    public Usuario get(Long id) {
        return repo.findById(id).orElse(null);
    }

    @Override
    public List<Usuario> get(String termoBusca) {
        return repo.findByAll(termoBusca);
    }

    @Override
    public Usuario save(Usuario objeto) {
        return repo.save(objeto);
    }

    @Override
    public void delete(Long id) {
        repo.deleteById(id);
    }

    public Usuario getByCpf(String cpf) {
        return repo.findByCpf(cpf);
    }

    public Usuario getByMatricula(String matricula) {
        return repo.findByCpf(matricula);
    }

}
