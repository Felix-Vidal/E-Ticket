package br.ufac.eticketapi.model;

import java.io.Serializable;
import java.util.Date;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class Usuario implements Serializable{
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(nullable = false, updatable = false)
    private Long id;

    @Column(nullable = false)
    private String nome;

    @Column(nullable = false)
    private String nomeSocial;

    @Column(nullable = false)
    private String matricula;

    @Column(nullable = false)
    private String classificacao;

    @Column(nullable = false)
    private String cpf;

    @Column(nullable = false)
    private Date dataEntrada;

    @Column(nullable = false)
    private String unidade;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private ESituacao situacao;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private EGratuidade gratuidade;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private EPapel papel;

    @Column(nullable = false)
    private boolean prioridade = true;

    @Column(nullable = false)
    private boolean ativo = true;




}
