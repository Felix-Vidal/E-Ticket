package br.ufac.eticketapi.service;

import java.util.List;

import org.springframework.stereotype.Service;

import br.ufac.eticketapi.model.Classificacao;
import br.ufac.eticketapi.repository.ClassificacaoRepository;

@Service
public class ClassificacaoService implements IService<Classificacao>{
    private final ClassificacaoRepository repo;

    public ClassificacaoService(ClassificacaoRepository repo) {
        this.repo = repo;
    }

    @Override
    public List<Classificacao> get() {
        return repo.findAll();
    }

    @Override
    public Classificacao get(Long id) {
        return repo.findById(id).orElse(null);
    }

    @Override
    public List<Classificacao> get(String termoBusca) {
        return repo.findByAll(termoBusca);
    }

    @Override
    public Classificacao save(Classificacao objeto) {
       return repo.save(objeto);
    }

    @Override
    public void delete(Long id) {
        repo.deleteById(id);
    }

}
