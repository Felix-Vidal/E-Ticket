package br.ufac.eticketapi.model;

import java.io.Serializable;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class Classificacao implements Serializable{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(nullable = false, updatable = false)
    private Long id;

    @Column(nullable = false)
    private String nome;

    @Column(nullable = false)
    private Double valorCafe;

    @Column(nullable = false)
    private Double valorAlmoco;

    @Column(nullable = false)
    private Double valorJanta;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getNome() {
        return nome;
    }

    public void setNome(String nome) {
        this.nome = nome;
    }

    public Double getValorCafe() {
        return valorCafe;
    }

    public void setValorCafe(Double valorCafe) {
        this.valorCafe = valorCafe;
    }

    public Double getValorAlmoco() {
        return valorAlmoco;
    }

    public void setValorAlmoco(Double valorAlmoco) {
        this.valorAlmoco = valorAlmoco;
    }

    public Double getValorJanta() {
        return valorJanta;
    }

    public void setValorJanta(Double valorJanta) {
        this.valorJanta = valorJanta;
    }
}
